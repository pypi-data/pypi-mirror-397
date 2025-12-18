class InputValidator:
    @staticmethod
    def validate_number_of_games(number_of_games: int) -> int:
        if not isinstance(number_of_games, int):
            raise TypeError("number_of_games deve ser um inteiro")
        
        if number_of_games < 1:
            raise ValueError("number_of_games deve ser maior que 0")
        
        if number_of_games > 500:
            raise ValueError("number_of_games não pode ser maior que 500")
        
        return number_of_games
    
    @staticmethod
    def validate_table_id(table_id: str) -> str:
        if not isinstance(table_id, str) or not table_id.strip():
            raise ValueError("table_id deve ser uma string não vazia")
        
        table_id = table_id.strip()
        if not all(c.isalnum() or c in '-_' for c in table_id):
            raise ValueError("table_id contém caracteres inválidos")
        
        return table_id
    
    @staticmethod
    def validate_fields(fields) -> list:
        if fields is not None and not isinstance(fields, list):
            raise TypeError("fields deve ser uma lista ou None")
        
        return fields
    
    @staticmethod
    def validate_email(email: str) -> str:
        if not email or not isinstance(email, str) or '@' not in email:
            raise ValueError("Email inválido")
        
        return email.strip().lower()
    
    @staticmethod
    def validate_user(user: str) -> str:
        if not user or not isinstance(user, str) or len(user.strip()) == 0:
            raise ValueError("User inválido")
        
        return user.strip()
    
    @staticmethod
    def validate_password(password: str) -> str:
        if not password or not isinstance(password, str) or len(password) < 3:
            raise ValueError("Senha inválida")
        
        return password
    
    @staticmethod
    def validate_license_code(license_code: str) -> str:
        if not license_code or not isinstance(license_code, str) or len(license_code.strip()) == 0:
            raise ValueError("Código de licença inválido")
        
        return license_code.strip()