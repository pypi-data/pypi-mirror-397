import hashlib
import json
import os
import time
import traceback
from typing import Optional, Dict, Any

from playwright.sync_api import sync_playwright, Page, Browser
import requests

from .session import ConnectSession
from .license import LicenseManager, LicenseInfo, SubscriptionInactiveError
from .config import SupabaseConfig, ConfigError
from .validators import InputValidator
from .cache_manager import CacheManager
from .error_handler import error_handler, ErrorContext

BASE_URL = "https://211.43.149.100/"
ERROR_FILE = "app.error"
CACHE_FILE = ".DO_NOT_DELET.json"
SESSION_TIMEOUT = 600
IFRAME_RETRY_ATTEMPTS = 50
IFRAME_RETRY_DELAY = 0.2
POPUP_CLOSE_TIMEOUT = 300
POPUP_RETRY_DELAY = 500


class AuthenticationError(Exception):
    pass


class SessionExpiredError(Exception):
    pass


class LoginClient:
    def __init__(
        self,
        email: str,
        user: str,
        password: str,
        license_code: str
    ) -> None:
        email = InputValidator.validate_email(email)
        user = InputValidator.validate_user(user)
        password = InputValidator.validate_password(password)
        license_code = InputValidator.validate_license_code(license_code)
        
        try:
            supabase_url = SupabaseConfig.get_url()
            supabase_key = SupabaseConfig.get_key()
        except ConfigError as e:
            raise ValueError(
                f"Credenciais do Supabase não configuradas. {str(e)}"
            ) from e
        
        try:
            license_info = LicenseManager.verify(
                email=email,
                user=user,
                password=password,
                license_code=license_code,
                supabase_url=supabase_url,
                supabase_key=supabase_key,
            )
        except SubscriptionInactiveError:
            print("\n" + "="*50)
            print("RENOVE SEU PLANO")
            print("="*50)
            print("Sua assinatura está inativa.")
            print("Entre em contato para renovar seu plano.")
            print("="*50 + "\n")
            raise
        
        self._print_license_info(license_info)
        
        self.user = user
        self.email = email
        self.password = password
        self.license_info = license_info
        self._jsessionid: Optional[str] = None
        self._session: ConnectSession = ConnectSession()
        self._cache_manager: CacheManager = CacheManager()
        self._browser: Optional[Browser] = None
        self._authenticated = False
        self._cache_key: str = self._get_cache_key(email)
        
        cached_jsessionid = self._get_cached_jsessionid()
        if cached_jsessionid:
            self._jsessionid = cached_jsessionid
            self._authenticated = True
        else:
            self._authenticate()
    
    def _print_license_info(self, license_info: LicenseInfo) -> None:
        print("SESSÃO AUTENTICADA")
        print(f"Email: {license_info.email}")
        print(f"Plano: {license_info.plan_type}")
        print(f"Expira em: {license_info.days_remaining} dias")
        print(f"Data de expiração: {license_info.expires_at.strftime('%d/%m/%Y')}")
        print("\n")
    
    def _get_cache_key(self, user: str) -> str:
        if not user or not isinstance(user, str):
            raise ValueError("Email inválido para geração de chave de cache")
        return hashlib.md5(user.encode('utf-8')).hexdigest()
    
    def _load_cache(self) -> Dict[str, Any]:
        if not os.path.exists(CACHE_FILE):
            return {}
        
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            if not isinstance(cache, dict):
                return {}
            
            validated_cache = {}
            for key, value in cache.items():
                if isinstance(value, dict) and all(k in value for k in ["id", "created_at", "expires_at"]):
                    if (isinstance(value.get("id"), str) and 
                        isinstance(value.get("created_at"), (int, float)) and
                        isinstance(value.get("expires_at"), (int, float))):
                        validated_cache[key] = value
            
            return validated_cache
            
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_cache(self, jsessionid: str) -> None:
        if not jsessionid or not isinstance(jsessionid, str):
            return
        
        try:
            cache = self._load_cache()
            current_time = time.time()
            
            cache[self._cache_key] = {
                "id": jsessionid,
                "created_at": current_time,
                "expires_at": current_time + SESSION_TIMEOUT
            }
            
            temp_file = f"{CACHE_FILE}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
            
            if os.path.exists(temp_file):
                os.replace(temp_file, CACHE_FILE)
        except Exception:
            pass
    
    def _get_cached_jsessionid(self) -> Optional[str]:
        cache = self._load_cache()
        cache_entry = cache.get(self._cache_key)
        
        if not cache_entry:
            return None
        
        if self._is_cache_valid(cache_entry):
            return cache_entry.get("id")
        else:
            return None
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        expires_at = cache_entry.get("expires_at", 0)
        current_time = time.time()
        return expires_at > current_time
    
    def _clear_cache(self) -> None:
        try:
            cache = self._load_cache()
            if self._cache_key in cache:
                del cache[self._cache_key]
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, indent=2)
        except Exception:
            pass
    
    def _authenticate(self) -> None:
        try:
            
            with sync_playwright() as p:
                self._browser = p.chromium.launch(headless=True)
                page = self._browser.new_page()
                
                try:
                    self._perform_login(page)
                    self._close_popups(page)
                    
                    self._open_iframe(page)
                    self._close_popups(page)
                    
                    jsessionid = self._extract_jsessionid(page)
                    if not jsessionid:
                        raise AuthenticationError("Não foi possível extrair o JSESSIONID")
                    
                    self._jsessionid = jsessionid
                    self._authenticated = True
                    
                    self._save_cache(jsessionid)
                    
                    self._open_lobby(page)
                    
                finally:
                    self._browser.close()
                    self._browser = None
                    
        except Exception as e:
            self._handle_auth_error(e)
            raise AuthenticationError(f"Falha na autenticação: {str(e)}") from e
    
    def _perform_login(self, page: Page) -> None:
        page.goto(BASE_URL)
        page.locator("#loginTabButton").click()
        
        user_field = page.get_by_role("textbox", name="Digite o Número do Celular/")
        user_field.fill(self.user)
        user_field.press("Tab")
        
        password_field = page.get_by_role("textbox", name="Insira a senha")
        password_field.fill(self.password)
        
        page.locator("#insideLoginSubmitClick").click()
        time.sleep(1)
    
    def _close_popups(self, page: Page) -> None:
        try:
            while True:
                popup_selectors = [
                    ".ui-dialog-close-box__icon > svg",
                    ".ui-dialog-close-box__icon > svg > use"
                ]
                
                popup_count = 0
                for selector in popup_selectors:
                    popups = page.locator(selector)
                    count = popups.count()
                    popup_count += count
                    
                    for i in range(count):
                        try:
                            popups.nth(i).click(timeout=POPUP_CLOSE_TIMEOUT)
                        except Exception:
                            pass
                
                if popup_count == 0:
                    break
                
                page.wait_for_timeout(POPUP_RETRY_DELAY)
                
        except Exception:
            pass
    
    def _open_iframe(self, page: Page) -> None:
        page.locator("#ui-tabs-1-3").get_by_role("img", name=".").click()
        page.get_by_role("heading", name="PP Jogo Ao Vivo").click()
        time.sleep(4)
    
    def _extract_jsessionid(self, page: Page) -> Optional[str]:
        frame = None
        
        for attempt in range(IFRAME_RETRY_ATTEMPTS):
            for f in page.frames:
                if "pragmaticplaylive" in f.url:
                    frame = f
                    break
            
            if frame:
                break
            
            time.sleep(IFRAME_RETRY_DELAY)
        
        if not frame:
            raise AuthenticationError("Não foi possível encontrar o iframe")
        
        ppg = frame.evaluate("() => sessionStorage.getItem('PPG')")
        if not ppg:
            raise AuthenticationError("PPG não encontrado no sessionStorage do iframe")
        
        try:
            ppg_json = json.loads(ppg)
            jsessionid = ppg_json.get("JSESSIONID")
            
            if not jsessionid:
                raise AuthenticationError("JSESSIONID não encontrado no PPG")
            
            return jsessionid
            
        except json.JSONDecodeError as e:
            raise AuthenticationError(f"Erro ao fazer parse do PPG: {str(e)}") from e
        except Exception as e:
            raise AuthenticationError(f"Erro ao extrair JSESSIONID do PPG: {str(e)}") from e
    
    def _open_lobby(self, page: Page) -> None:
        try:
            page.locator("section div").filter(has_text="Lobby").click()
            time.sleep(3)
        except Exception:
            pass
    
    def _handle_auth_error(self, error: Exception) -> None:
        try:
            with open(ERROR_FILE, "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except Exception:
            pass
    
    def _ensure_authenticated(self) -> None:
        if not self._authenticated or not self._jsessionid:
            cached_jsessionid = self._get_cached_jsessionid()
            if cached_jsessionid:
                self._jsessionid = cached_jsessionid
                self._authenticated = True
            else:
                self._authenticate()
        else:
            cache_entry = self._load_cache().get(self._cache_key)
            if cache_entry and not self._is_cache_valid(cache_entry):
                self._clear_cache()
                self._authenticated = False
                self._jsessionid = None
                self._authenticate()
    
    def _handle_api_error(self, response: requests.Response) -> None:
        auth_error_codes = [401, 403]
        
        if response.status_code in auth_error_codes:
            self._clear_cache()
            self._authenticated = False
            self._jsessionid = None
            
            try:
                self._authenticate()
            except Exception as e:
                raise SessionExpiredError(
                    f"Falha ao re-autenticar após expiração de sessão: {str(e)}"
                ) from e
        else:
            raise Exception(
                f"Erro ao obter histórico (HTTP {response.status_code}): {response.text}"
            )
    
    def get_history(
        self,
        table_id: str,
        number_of_games: int = 100
    ) -> Dict[str, Any]:
        if not isinstance(table_id, str) or not table_id.strip():
            raise ValueError("table_id deve ser uma string não vazia")
        
        table_id = table_id.strip()
        if not all(c.isalnum() or c in '-_' for c in table_id):
            raise ValueError("table_id contém caracteres inválidos")
        
        if not isinstance(number_of_games, int):
            raise TypeError("number_of_games deve ser um inteiro")
        
        if number_of_games < 1:
            raise ValueError("number_of_games deve ser maior que 0")
        
        if number_of_games > 500:
            raise ValueError("number_of_games não pode ser maior que 500")
        
        self._ensure_authenticated()
        
        params = {
            "JSESSIONID": self._jsessionid,
            "tableId": table_id,
            "numberOfGames": number_of_games,
        }
        
        try:
            response = self._session.get("statisticHistory", params=params)
            
            if response.status_code != 200:
                self._handle_api_error(response)
                params["JSESSIONID"] = self._jsessionid
                response = self._session.get("statisticHistory", params=params)
                
                if response.status_code != 200:
                    raise Exception(
                        f"Erro ao obter histórico após re-autenticação "
                        f"(HTTP {response.status_code}): {response.text}"
                    )
            
            return response.json()
            
        except SessionExpiredError:
            raise
        except Exception as e:
            if isinstance(e, SessionExpiredError):
                raise
            try:
                with open(ERROR_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n{traceback.format_exc()}")
            except Exception:
                pass
            raise
    
    def get_jsessionid(self) -> Optional[str]:
        return self._jsessionid
    
    def is_authenticated(self) -> bool:
        return self._authenticated and self._jsessionid is not None
    
    def close(self) -> None:
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
            finally:
                self._browser = None


class StatisticHistoryClient:
    def __init__(self, session: ConnectSession, jsessionid: str) -> None:
        self.session = session
        self.jsessionid = jsessionid
    
    def get_history(
        self,
        table_id: str,
        number_of_games: int = 100
    ) -> Dict[str, Any]:
        params = {
            "JSESSIONID": self.jsessionid,
            "tableId": table_id,
            "numberOfGames": number_of_games,
        }
        response = self.session.get("statisticHistory", params=params)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao obter histórico (HTTP {response.status_code}): {response.text}"
            )
        return response.json()
