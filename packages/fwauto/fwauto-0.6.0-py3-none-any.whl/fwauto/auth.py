# -*- coding: utf-8 -*-
"""
FWAuto Authentication Module

用戶認證與 token 管理：
1. 檢查本地是否有有效的 user_token
2. 沒有則開啟瀏覽器進行 Google SSO 登入
3. 登入後儲存 token 到本地
4. 提供 token 給其他模組使用（如用量回報）
"""

import json
import os
import sys
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlparse
from typing import Optional

import requests

from .logging_config import get_logger

# ============================================================
# API 模式
# ============================================================


def is_direct_api_mode() -> bool:
    """
    檢查是否使用直連模式（Claude Max 訂閱）。

    當環境變數 FWAUTO_API_MODE=direct 時，使用本機 Claude Max 訂閱，
    繞過 API proxy，適用於開發和測試環境。

    Returns:
        bool: True 表示使用直連模式
    """
    return os.environ.get("FWAUTO_API_MODE", "").lower() == "direct"


# ============================================================
# 配置
# ============================================================

# FWAuto Server URL
FWAUTO_SERVER_URL = "https://fwauto-server-189969833984.asia-east1.run.app"

# 本地配置檔案路徑
AUTH_CONFIG_FILE = Path.home() / ".fwauto_auth.json"

# 本地 callback server port
CALLBACK_PORT = 8888

# 登入超時時間（秒）
LOGIN_TIMEOUT = 300


# ============================================================
# Callback Handler
# ============================================================

class _AuthCallbackHandler(BaseHTTPRequestHandler):
    """處理 OAuth 回調"""
    auth_result = None

    def do_GET(self):
        """處理 GET 請求"""
        if self.path.startswith('/callback'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)

            if 'user_token' in params and 'email' in params:
                _AuthCallbackHandler.auth_result = {
                    'user_token': params['user_token'][0],
                    'email': params['email'][0],
                    'name': params.get('name', [params['email'][0].split('@')[0]])[0]
                }

                # 返回成功頁面
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>FWAuto - 登入成功</title>
                    <style>
                        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                               text-align: center; padding: 50px; background: #f5f5f5; }
                        .container { background: white; padding: 40px; border-radius: 10px;
                                    max-width: 500px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        .success { color: #4CAF50; font-size: 48px; margin: 0; }
                        h1 { color: #333; margin: 20px 0; }
                        p { color: #666; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success">✅</div>
                        <h1>登入成功！</h1>
                        <p>您可以關閉此視窗，返回終端機繼續使用 FWAuto。</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"<h1>Login failed</h1>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """禁用日誌輸出"""
        pass


# ============================================================
# 認證管理
# ============================================================

class AuthManager:
    """FWAuto 認證管理器"""

    def __init__(self, server_url: str = FWAUTO_SERVER_URL):
        self.server_url = server_url
        self.config_file = AUTH_CONFIG_FILE
        self._user_token: Optional[str] = None
        self._user_email: Optional[str] = None
        self._user_name: Optional[str] = None
        self.logger = get_logger("auth")

    def _load_config(self) -> bool:
        """從本地載入配置"""
        if not self.config_file.exists():
            return False

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._user_token = config.get('user_token')
                self._user_email = config.get('email')
                self._user_name = config.get('name')
                return bool(self._user_token)
        except Exception as e:
            self.logger.debug(f"Failed to load auth config: {e}")
            return False

    def _save_config(self):
        """儲存配置到本地"""
        try:
            config = {
                'user_token': self._user_token,
                'email': self._user_email,
                'name': self._user_name,
                'server_url': self.server_url
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Auth config saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save auth config: {e}")

    def _verify_token(self) -> bool:
        """驗證 token 是否有效"""
        if not self._user_token:
            return False

        try:
            response = requests.get(
                f"{self.server_url}/api/usage",
                headers={"Authorization": f"Bearer {self._user_token}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _do_login(self, use_dev_login: bool = False) -> bool:
        """執行登入流程"""
        print()
        print("=" * 60)
        print("🔐 FWAuto 需要登入")
        print("=" * 60)
        print()

        # 重置 callback handler 的狀態
        _AuthCallbackHandler.auth_result = None

        # 啟動本地 callback server
        try:
            server = HTTPServer(('localhost', CALLBACK_PORT), _AuthCallbackHandler)
        except OSError as e:
            print(f"❌ 無法啟動 callback server (port {CALLBACK_PORT}): {e}")
            return False

        server_thread = Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        # 建構登入 URL
        callback_url = f"http://localhost:{CALLBACK_PORT}/callback"

        if use_dev_login:
            login_url = f"{self.server_url}/auth/dev-login?email=dev@example.com&callback={callback_url}"
            print("🔧 使用開發模式登入...")
        else:
            login_url = f"{self.server_url}/auth/login?callback={callback_url}"
            print("📝 登入流程:")
            print("   1. 開啟瀏覽器進行 Google 登入")
            print("   2. 登入成功後自動返回")
            print()

        print(f"🌐 正在開啟瀏覽器...")
        webbrowser.open(login_url)

        print()
        print("⏳ 等待登入...")
        if not use_dev_login:
            print("   (請在瀏覽器中完成登入)")
        print()

        # 等待回調
        start_time = time.time()
        while _AuthCallbackHandler.auth_result is None:
            if time.time() - start_time > LOGIN_TIMEOUT:
                print("❌ 登入超時")
                server.shutdown()
                return False
            time.sleep(0.5)

        # 關閉 server
        server.shutdown()

        # 處理結果
        result = _AuthCallbackHandler.auth_result
        self._user_token = result['user_token']
        self._user_email = result['email']
        self._user_name = result['name']

        print("=" * 60)
        print("✅ 登入成功！")
        print("=" * 60)
        print(f"   用戶: {self._user_name} ({self._user_email})")
        print()

        # 儲存配置
        self._save_config()

        return True

    def ensure_authenticated(self, use_dev_login: bool = False) -> bool:
        """
        確保用戶已認證

        Args:
            use_dev_login: 是否使用開發模式登入（不需要 Google OAuth）

        Returns:
            bool: 是否認證成功
        """
        # 1. 嘗試載入本地配置
        if self._load_config():
            # 2. 驗證 token 是否有效
            if self._verify_token():
                self.logger.debug(f"Authenticated as {self._user_email}")
                return True
            else:
                self.logger.debug("Token expired or invalid")

        # 3. 需要登入
        return self._do_login(use_dev_login=use_dev_login)

    @property
    def user_token(self) -> Optional[str]:
        """取得 user token"""
        return self._user_token

    @property
    def user_email(self) -> Optional[str]:
        """取得用戶 email"""
        return self._user_email

    @property
    def user_name(self) -> Optional[str]:
        """取得用戶名稱"""
        return self._user_name

    @property
    def is_authenticated(self) -> bool:
        """檢查是否已認證"""
        return bool(self._user_token)

    def logout(self):
        """登出（清除本地配置）"""
        self._user_token = None
        self._user_email = None
        self._user_name = None

        if self.config_file.exists():
            self.config_file.unlink()
            print("✅ 已登出，配置已清除")


# ============================================================
# 全域實例
# ============================================================

# 全域 AuthManager 實例
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """取得全域 AuthManager 實例"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


def get_user_token() -> Optional[str]:
    """
    取得當前用戶的 token

    這是給其他模組（如 ai_brain.py）使用的簡便函數
    """
    # 先嘗試從已載入的 AuthManager 取得
    if _auth_manager and _auth_manager.user_token:
        return _auth_manager.user_token

    # 否則從配置檔案讀取
    if AUTH_CONFIG_FILE.exists():
        try:
            with open(AUTH_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('user_token')
        except Exception:
            pass

    return None


def get_auth_server_url() -> str:
    """取得認證伺服器 URL"""
    if AUTH_CONFIG_FILE.exists():
        try:
            with open(AUTH_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('server_url', FWAUTO_SERVER_URL)
        except Exception:
            pass
    return FWAUTO_SERVER_URL


# ============================================================
# CLI 入口
# ============================================================

def cli_login(dev: bool = False):
    """CLI 登入命令"""
    auth = get_auth_manager()
    auth.ensure_authenticated(use_dev_login=dev)


def cli_logout():
    """CLI 登出命令"""
    auth = get_auth_manager()
    auth.logout()


def cli_status():
    """CLI 顯示登入狀態"""
    auth = get_auth_manager()

    if auth._load_config():
        print()
        print("📋 FWAuto 認證狀態")
        print("=" * 40)
        print(f"   狀態: ✅ 已登入")
        print(f"   用戶: {auth.user_name}")
        print(f"   Email: {auth.user_email}")
        print(f"   伺服器: {auth.server_url}")
        print(f"   Dashboard: {auth.server_url}/dashboard")
        print()

        # 驗證 token
        if auth._verify_token():
            print("   Token: ✅ 有效")
        else:
            print("   Token: ⚠️ 已失效，請重新登入")
        print()
    else:
        print()
        print("📋 FWAuto 認證狀態")
        print("=" * 40)
        print("   狀態: ❌ 未登入")
        print()
        print("   執行 'fwauto auth login' 進行登入")
        print(f"   Dashboard: {FWAUTO_SERVER_URL}/dashboard")
        print()
