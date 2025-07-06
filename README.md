# WellBoard - マルチテナント チーム ウェルネス追跡システム

WellBoardは、組織がチームメンバーのモチベーションやストレスレベルを含むウェルネスを追跡・管理するための包括的なフルスタックウェブアプリケーションです。マルチテナントアーキテクチャにより、複数の組織が独立してデータを管理できます。

## 🏗️ アーキテクチャ

- **フロントエンド**: Vue 3 + Vuetify 3 + Pinia（ステート管理）
- **バックエンド**: Django REST Framework + JWT認証
- **データベース**: SQLite（開発）/ PostgreSQL（本番推奨）
- **認証**: JWT（クッキーベース）
- **AI機能**: AWS Bedrock （モチベーションやストレススコア自動計算）

## 📁 プロジェクト構造

```
well-board/
├── frontend/               # Vue.js フロントエンドアプリケーション
│   ├── api/               # APIクライアント設定
│   ├── components/        # 再利用可能なVueコンポーネント
│   ├── pages/            # ルート別Vueコンポーネント
│   ├── stores/           # Piniaステート管理
│   └── router/           # Vue Router設定
├── backend/               # Django バックエンドAPI
│   ├── models/           # データモデル（テナント分離）
│   ├── serializers/      # データシリアライゼーション
│   ├── views/            # APIエンドポイント
│   ├── authentication.py # カスタムJWT認証
│   └── permissions.py    # テナント分離権限
├── config/               # Django設定
    └── settings/         # 環境別設定（dev, prod）
```

## 🚀 クイックスタート

### 前提条件
- Python 3.8+
- Node.js 14+
- npm または yarn

### 1. リポジトリをクローン
```bash
git clone <repository-url>
cd well-board
```

### 2. バックエンド設定
```bash
# 仮想環境を作成・アクティベート
python -m venv venv 
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate   # Windows

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してデータベースとJWT設定を追加

# データベースマイグレーション
python manage.py migrate

# スーパーユーザーを作成（オプション）
python manage.py createsuperuser
```

### 3. フロントエンド設定
```bash
# 依存関係をインストール
npm install
```

### 4. 開発サーバーを起動

**ターミナル1（バックエンド）:**
```bash
python manage.py runserver 8081
```

**ターミナル2（フロントエンド）:**
```bash
npm run dev
```

アプリケーションは http://localhost:XXXX でアクセス可能です（起動時に表示されます）。
API は http://localhost:8081 で動作します。

## 🔧 開発コマンド

### バックエンド（Django）
```bash
python manage.py runserver 8081      # 開発サーバー起動
python manage.py test                # テスト実行
python manage.py makemigrations      # マイグレーションファイル作成
python manage.py migrate             # マイグレーション実行
python manage.py shell               # Djangoシェル
```

### フロントエンド（Vue/Vuetify）
```bash
npm run dev          # 開発サーバー起動（localhost:3000）
npm run build        # 本番用ビルド
npm run lint         # ESLint実行（--fix付き）
npm run type-check   # TypeScript型チェック
npm run preview      # 本番ビルドプレビュー
```

## 🏢 マルチテナント機能

### テナント分離
- すべてのデータモデルは `tenant` 外部キーを持つ
- ユーザーは単一のテナントに属する
- APIリクエストは自動的にテナントでフィルタリング

### データモデル階層
```
Tenant（組織）
├── Users（ユーザー：SUPERUSER, ADMIN, MANAGER, USER）
├── Teams（チーム：JSON質問設定付き）
└── Entry（記録：AIスコア付き）
```

## 🤖 AI統合

### AWS Bedrock統合
- **機能**: アンケート回答の自動スコア計算（0-100）
- **用途**: チームウェルネス分析とトレンド把握

## 🔐 認証・セキュリティ

### JWT認証
- クッキーベースのJWTトークン
- カスタム認証クラス `CustomJWTAuthentication`
- セキュアなクッキー処理

### 権限システム
- テナント分離権限クラス
- ロールベースアクセス制御
- APIエンドポイント毎の権限チェック

## 🧪 テスト

### バックエンドテスト
```bash
python manage.py test                    # 全テスト実行
python manage.py test tests.views.test_view  # 特定テスト実行
```

テストフォーカス：
- テナント分離機能
- 権限システム
- 認証フロー
- APIエンドポイント

## 🌐 本番デプロイ

### 環境設定
- `config/settings/prod.py` を使用
- AWS認証情報設定

### 静的ファイル
```bash
# フロントエンドビルド
cd frontend && npm run build

# Django静的ファイル収集
python manage.py collectstatic
```

## 📊 主要機能

### データ管理
- チーム概要とメンバー管理
- チーム毎のカスタム質問設定
- 質問に対する回答記録・追跡

### データ可視化
- 時系列データ表示
- チーム比較機能

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。
