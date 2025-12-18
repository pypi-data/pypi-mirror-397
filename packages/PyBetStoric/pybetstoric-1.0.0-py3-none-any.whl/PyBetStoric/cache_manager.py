import json
import os
import time
import hashlib
from typing import Dict, Any, Optional
from .error_handler import ErrorContext

CACHE_FILE = ".DO_NOT_DELET.json"
SESSION_TIMEOUT = 600

class CacheManager:
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self.session_timeout = SESSION_TIMEOUT
    
    def get_cache_key(self, identifier: str) -> str:
        if not identifier or not isinstance(identifier, str):
            raise ValueError("Identificador inválido para geração de chave de cache")
        
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()
    
    def load_cache(self) -> Dict[str, Any]:
        if not os.path.exists(self.cache_file):
            return {}
        
        with ErrorContext("load_cache", suppress=True) as ctx:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            if not isinstance(cache, dict):
                return {}
            
            validated_cache = {}
            for key, value in cache.items():
                if self._is_valid_cache_entry(value):
                    validated_cache[key] = value
            
            return validated_cache
        
        return {}
    
    def save_cache(self, cache_key: str, session_id: str) -> bool:
        if not session_id or not isinstance(session_id, str):
            return False
        
        with ErrorContext("save_cache", suppress=True) as ctx:
            cache = self.load_cache()
            current_time = time.time()
            
            cache[cache_key] = {
                "id": session_id,
                "created_at": current_time,
                "expires_at": current_time + self.session_timeout
            }
            
            temp_file = f"{self.cache_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
            
            if os.path.exists(temp_file):
                os.replace(temp_file, self.cache_file)
                return True
        
        return False
    
    def get_cached_session(self, cache_key: str) -> Optional[str]:
        cache = self.load_cache()
        cache_entry = cache.get(cache_key)
        
        if not cache_entry:
            return None
        
        if self.is_cache_valid(cache_entry):
            return cache_entry.get("id")
        
        return None
    
    def is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        expires_at = cache_entry.get("expires_at", 0)
        current_time = time.time()
        return expires_at > current_time
    
    def clear_cache(self, cache_key: str) -> bool:
        with ErrorContext("clear_cache", suppress=True) as ctx:
            cache = self.load_cache()
            if cache_key in cache:
                del cache[cache_key]
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, indent=2)
                return True
        
        return False
    
    def clear_all_cache(self) -> bool:
        with ErrorContext("clear_all_cache", suppress=True) as ctx:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                return True
        
        return False
    
    def cleanup_expired(self) -> int:
        cache = self.load_cache()
        original_count = len(cache)
        
        valid_cache = {
            key: value for key, value in cache.items()
            if self.is_cache_valid(value)
        }
        
        with ErrorContext("cleanup_expired", suppress=True) as ctx:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(valid_cache, f, indent=2)
        
        return original_count - len(valid_cache)
    
    def _is_valid_cache_entry(self, entry: Any) -> bool:
        if not isinstance(entry, dict):
            return False
        
        required_fields = ["id", "created_at", "expires_at"]
        if not all(field in entry for field in required_fields):
            return False
        
        return (isinstance(entry.get("id"), str) and 
                isinstance(entry.get("created_at"), (int, float)) and
                isinstance(entry.get("expires_at"), (int, float)))