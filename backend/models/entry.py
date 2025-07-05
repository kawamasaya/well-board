
import datetime
import json
import logging

from botocore.exceptions import ClientError
from django.db import models

from .team import Team
from .tenant import Tenant
from .user import User


class Entry(models.Model):
    """
    チームメンバーのモチベーション・ストレス記録エントリーモデル
    
    各ユーザーが日次でチームの質問に回答し、AWS BedrockのAIが
    回答内容を分析してストレス度・モチベーション度を自動計算する。
    
    Attributes:
        tenant (ForeignKey): 所属テナント（組織）
        user (ForeignKey): 記録者ユーザー
        team (ForeignKey): 所属チーム
        questions (JSONField): チーム固有の質問項目
        answers (JSONField): ユーザーの回答内容
        stress_score (IntegerField): AIが計算したストレス度 (0-100)
        motivation_score (IntegerField): AIが計算したモチベーション度 (0-100)
        reported_at (DateField): 記録日（デフォルト: 今日）
        
    Constraints:
        - 1日1エントリーの制約: (tenant, user, team, reported_at)でユニーク
        
    AI Integration:
        - save()時に自動でAWS Bedrockを呼び出し
        - answersが存在する場合のみAI計算実行
        - 計算失敗時はデフォルト値(0)を設定
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    questions = models.JSONField(blank=True, null=True)
    answers = models.JSONField(blank=True, null=True)
    stress_score = models.IntegerField(null=True, blank=True)
    motivation_score = models.IntegerField(null=True, blank=True)
    reported_at = models.DateField(default=datetime.date.today)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'user', 'team', 'reported_at'],
                name='unique_entry_per_day'
            )
        ]
        indexes = [
            models.Index(fields=['tenant', 'reported_at'], name='entry_tenant_date_idx'),
            models.Index(fields=['tenant', 'team', 'reported_at'], name='entry_tenant_team_date_idx'),
            models.Index(fields=['tenant', 'user', 'reported_at'], name='entry_tenant_user_date_idx'),
        ]
        
    def save(self, *args, **kwargs):
        # AI計算を試行し、失敗してもデータ保存は継続
        try:
            if self.answers:  # answersがある場合のみAI計算を実行
                scores = self.calculate_scores()
                self.stress_score = scores.get('stress_score', 0)
                self.motivation_score = scores.get('motivation_score', 0)
            else:
                # answersがない場合はデフォルト値を設定
                self.stress_score = 0
                self.motivation_score = 0
        except (ClientError, json.JSONDecodeError, KeyError) as e:
            # AI計算失敗時はログ出力してデフォルト値を設定
            logger = logging.getLogger(__name__)
            logger.error(f"AI score calculation failed: {type(e).__name__}: {e}")
            self.stress_score = 0
            self.motivation_score = 0
        except Exception as e:
            # 予期しないエラーは重要度を上げてログ
            logger = logging.getLogger(__name__)
            logger.critical(f"Unexpected error in AI calculation: {e}")
            self.stress_score = 0
            self.motivation_score = 0
        
        super().save(*args, **kwargs)
    
    def calculate_scores(self):
        """
        AWS Bedrockを使用してストレス度とモチベーション度を計算する
        
        質問と回答のJSONデータをAmazon Nova Microモデルに送信し、
        0-100のスケールでストレス度とモチベーション度を採点する。
        
        Returns:
            dict: 以下の形式の辞書
                - stress_score (int): ストレス度 (0-100)
                - motivation_score (int): モチベーション度 (0-100)  
                - stress_reason (str): ストレス度の理由 (30字以内)
                - motivation_reason (str): モチベーション度の理由 (30字以内)
                
        Raises:
            ClientError: AWS Bedrock API呼び出しエラー
            JSONDecodeError: レスポンスのJSONパースエラー
            KeyError: 必要なキーが存在しないエラー
            
        Note:
            - リージョン: us-west-2
            - モデル: us.amazon.nova-micro-v1:0
            - エラー時はデフォルト値（0）を返す
        """
        
        import json

        from boto3 import client
        from botocore.exceptions import ClientError

        bedrock_client = client("bedrock-runtime", region_name="us-west-2")
        model_id = "us.amazon.nova-micro-v1:0"

        extracted_questions = "\n".join([f"{k}: {v}" for k,v in self.questions.items()])
        extracted_answers = "\n".join([f"{k}: {v}" for k,v in self.answers.items()])

        user_message = f"""
以下の質問と回答から、ストレス度とモチベーション度をそれぞれ0-100で採点し、JSON形式で出力してください。説明不要です。
- ストレス度: ストレスが高い場合は数値を高く採点する
- モチベーション度: モチベーションが高い場合は数値を高く採点する
- 各項目について「reason」は30字以内で簡潔に

質問:
{extracted_questions}

回答:
{extracted_answers}

出力形式:
{{"stress_score": 数値, "stress_reason": "ストレス説明", "motivation_score": 数値, "motivation_reason": "モチベーション説明"}}
"""

        conversation = [
            {
                "role": "user",
                "content": [{"text": user_message}],
            }
        ]

        try:
            response = bedrock_client.converse(
                modelId=model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 512, "temperature": 0, "topP": 0.9},
            )

            response_text = response["output"]["message"]["content"][0]["text"]
            json_data = json.loads(response_text)
            
            return json_data

        except (ClientError, Exception) as e:
            logger = logging.getLogger(__name__)
            logger.error(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            # デフォルト値を返す
            return {
                'stress_score': 0,
                'motivation_score': 0,
                'stress_reason': '計算エラー',
                'motivation_reason': '計算エラー'
            }