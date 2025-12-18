import traceback
import functools
from typing import Callable, Any

ERROR_FILE = "app.error"

def error_handler(log_errors: bool = True, reraise: bool = True):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    _log_error(func.__name__, e)
                
                if reraise:
                    raise
                
                return None
        return wrapper
    return decorator

def _log_error(function_name: str, error: Exception) -> None:
    try:
        error_info = f"\n{'='*50}\n"
        error_info += f"ERRO EM: {function_name}\n"
        error_info += f"TIPO: {type(error).__name__}\n"
        error_info += f"MENSAGEM: {str(error)}\n"
        error_info += f"TRACEBACK:\n{traceback.format_exc()}\n"
        error_info += f"{'='*50}\n"
        
        with open(ERROR_FILE, "a", encoding="utf-8") as f:
            f.write(error_info)
    except Exception:
        pass

class ErrorContext:
    def __init__(self, operation_name: str, log_errors: bool = True, suppress: bool = False):
        self.operation_name = operation_name
        self.log_errors = log_errors
        self.suppress = suppress
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            
            if self.log_errors:
                _log_error(self.operation_name, exc_val)
            
            return self.suppress
        
        return False
    
    def has_error(self) -> bool:
        return self.error is not None
    
    def get_error(self) -> Exception:
        return self.error