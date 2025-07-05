
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """
    Cookie ベース JWT 認証クラス
    
    JWT認証をCookie経由で実行するカスタム認証。
    Authorizationヘッダーの代わりにHTTPCookieからトークンを取得。
            
    Cookie Name:
        - "access_token": JWT アクセストークンを格納
        
    Flow:
        1. リクエストのCookieから"access_token"を取得
        2. トークンの検証（署名、有効期限等）
        3. ユーザー情報の取得・返却
        
    Returns:
        tuple: (User, validated_token) または None
    """

    def authenticate(self, request):
        """
        Cookieから JWT トークンを取得して認証を実行
        
        Args:
            request: HTTPリクエストオブジェクト
            
        Returns:
            tuple: (User, validated_token) 認証成功時
        """
        access_token = request.COOKIES.get("access_token")
        if access_token is None:
            return None

        validated_token = self.get_validated_token(access_token)
        return self.get_user(validated_token), validated_token