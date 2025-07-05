
import os
from environ import Env

from .base import *

# 環境変数を読み込む
env = Env()

SECRET_KEY = env("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=['mydomain.com'])

# CORS設定（本番環境用）
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
    "https://mydomain.com",
    "https://www.mydomain.com",
])
CORS_ALLOW_CREDENTIALS = True

# JWT設定（本番環境用）
SIMPLE_JWT.update({
    "AUTH_COOKIE_SECURE": True,  # HTTPS環境でのみCookie送信
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),  # 本番では短めに設定
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
})