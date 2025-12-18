import base64
import hashlib


class ConfigError(Exception):
    pass


class SupabaseConfig:
    _x1: str = "Y0hsaVpYUnBjM1J2Y21salgzTmhiSFJvZEhSd2N6b3ZMM1p3YW0xeFpISjRaM05rYm1oMmFHaHFkbnAzTG5OMWNHRmlZWE5sTG1OdmNETndjRE55WHpJd01qUT0="
    _x2: str = "Y0hsaVpYUnBjM1J2Y21salgzTmhiSFJsZVVwb1lrZGphVTlwU2tsVmVra3hUbWxKYzBsdVVqVmpRMGsyU1d0d1dGWkRTamt1WlhsS2NHTXpUV2xQYVVwNlpGaENhRmx0Um5wYVUwbHpTVzVLYkZwcFNUWkpibHAzWVcweGVGcElTalJhTTA1clltMW9NbUZIYUhGa2JuQXpTV2wzYVdOdE9YTmFVMGsyU1cxR2RXSXlOR2xNUTBwd1dWaFJhVTlxUlROT2FsVXdUbXBqZVUxcVJYTkpiVlkwWTBOSk5rMXFRVFJOVkVFd1RYcEplVTFZTUM1clZqVkVNbFl3TUVWd2FuWmhTSGxrVUZaeFRXeFNNelJSVEdoT1RrOXJVbEp2Y2twUFFYUkJlVVk0Y0ROd2NETnlYekl3TWpRPQ=="
    _s: str = "cHliZXRpc3RvcmljX3NhbHQ="
    _p: str = "cDNwcDNyXzIwMjQ="
    
    @classmethod
    def _d(cls, data: str) -> str:
        try:
            l1 = base64.b64decode(data).decode('utf-8')
            l2 = base64.b64decode(l1).decode('utf-8')
            s = base64.b64decode(cls._s).decode('utf-8')
            p = base64.b64decode(cls._p).decode('utf-8')
            if l2.startswith(s) and l2.endswith(p):
                return l2[len(s):-len(p)]
            return l2
        except Exception:
            raise ConfigError("Falha na decodificação")
    
    @classmethod
    def get_url(cls) -> str:
        try:
            return cls._d(cls._x1)
        except Exception as e:
            raise ConfigError(f"Erro de configuração: {e}")
    
    @classmethod
    def get_key(cls) -> str:
        try:
            return cls._d(cls._x2)
        except Exception as e:
            raise ConfigError(f"Erro de configuração: {e}")