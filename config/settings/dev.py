import os
from pathlib import Path

from environ import Env  # 

from .base import *

# 環境変数を読み込む
env = Env()
# .env ファイルを読み込む
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
env.read_env(env_file=os.path.join(BASE_DIR, ".env"))  

SECRET_KEY = env("SECRET_KEY")

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

SIMPLE_JWT.update({
    "AUTH_COOKIE_SECURE": False,
})

# CORS設定（開発環境用）
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
CORS_ALLOW_CREDENTIALS = True

IS_LOCAL = True