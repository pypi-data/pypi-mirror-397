from .client import StatisticHistoryClient, LoginClient
from .validators import InputValidator

class _LoginClientWrapper:
    def __init__(self, login_client: LoginClient):
        self._login_client = login_client
        self.session = login_client._session
        self.jsessionid = login_client.get_jsessionid()
    
    def get_history(self, table_id: str, number_of_games: int = 100):
        return self._login_client.get_history(table_id, number_of_games)

class BaseGame:
    NUMBER_OF_GAMES = 100
    REPEAT = 1
    INTERVAL = None
    
    def __init__(self, client: StatisticHistoryClient):
        self.client = client

    def _parse_history(self, data: dict, fields: list = None, number_of_games: int = 100):
        history = data.get("history", [])
        if not history:
            return []

        resultados = []
        for idx, game in enumerate(history[:number_of_games], start=1):
            rodada = {field: game.get(field) for field in fields} if fields else dict(game)
            rodada["Rodada"] = idx
            resultados.append(rodada)

        return resultados

    def _get_game_history(self, table_id: str, fields: list, number_of_games: int = 100):
        number_of_games = InputValidator.validate_number_of_games(number_of_games)
        fields = InputValidator.validate_fields(fields)
        
        data = self.client.get_history(table_id, number_of_games)
        return self._parse_history(data, fields=fields, number_of_games=number_of_games)
    
    def _execute_with_repeat(self, method_func, repeat=None, interval=None):
        import time
        
        repeat = repeat or self.REPEAT
        interval = interval or self.INTERVAL
        
        if repeat != 1 and interval is None:
            raise ValueError("Parâmetro 'interval' é obrigatório quando repeat > 1")
        
        if repeat == 1:
            return method_func()
        
        def _generator():
            is_infinite = repeat == "i"
            count = 0
            
            try:
                while is_infinite or count < repeat:
                    yield method_func()
                    count += 1
                    
                    if not is_infinite and count >= repeat:
                        break
                    
                    if interval and interval > 0:
                        time.sleep(interval)
                        
            except KeyboardInterrupt:
                print(f"\nExecução interrompida pelo usuário após {count} chamadas")
        
        return _generator()
    
    @staticmethod
    def format_results(results, show_round_number=True, compact=False):
        if not results:
            return "Nenhum resultado encontrado"
        
        if not isinstance(results, list):
            return "Resultado inválido"
        
        formatted_lines = []
            
        for i, result in enumerate(results, 1):
            if compact:
                round_num = result.get('Rodada', i)
                main_result = BaseGame._get_main_result(result)
                formatted_lines.append(f"Rodada {round_num:2d}: {main_result}")
            else:
                if show_round_number and 'Rodada' in result:
                    formatted_lines.append(f"\nRODADA {result['Rodada']}:")
                elif show_round_number:
                    formatted_lines.append(f"\nRODADA {i}:")
                else:
                    formatted_lines.append(f"\nRESULTADO {i}:")
                
                for key, value in result.items():
                    if key != 'Rodada':
                        formatted_lines.append(f"   {key}: {value}")
        
        if show_round_number and not compact:
            formatted_lines.append("\n" + "=" * 70)
        
        return "\n".join(formatted_lines)
    
    @staticmethod
    def _get_main_result(result):
        fields = []
        count = 0
        max_fields = 4
        
        for key, value in result.items():
            if key != 'Rodada' and count < max_fields:
                fields.append(f"{key}: {value}")
                count += 1
        
        if fields:
            return " | ".join(fields)
        
        return "Sem dados"
    
    @staticmethod
    def print_json(results):
        import json
        import types
        
        if isinstance(results, types.GeneratorType):
            for i, resultado in enumerate(results, 1):
                print(f"\nEXECUÇÃO {i}:")
                if not resultado:
                    print("Nenhum resultado encontrado")
                    continue
                
                if not isinstance(resultado, list):
                    print("Resultado inválido")
                    continue
                
                print("[", end="")
                for j, result in enumerate(resultado):
                    if j > 0:
                        print(",", end="")
                    print(f"\n{json.dumps(result, ensure_ascii=False)}", end="")
                print("\n]")
        else:
            if not results:
                print("Nenhum resultado encontrado")
                return
            
            if not isinstance(results, list):
                print("Resultado inválido")
                return
            
            print("[", end="")
            for i, result in enumerate(results):
                if i > 0:
                    print(",", end="")
                print(f"\n{json.dumps(result, ensure_ascii=False)}", end="")
            print("\n]")
    
    @staticmethod
    def print_results(results, show_round_number=True, compact=False):
        import types
        
        if isinstance(results, types.GeneratorType):
            for i, resultado in enumerate(results, 1):
                print(f"\nEXECUÇÃO {i}:")
                print(BaseGame.format_results(resultado, show_round_number, compact))
        else:
            print(BaseGame.format_results(results, show_round_number, compact))
    
    @staticmethod
    def print_compact(results):
        import types
        
        if isinstance(results, types.GeneratorType):
            for i, resultado in enumerate(results, 1):
                print(f"\nEXECUÇÃO {i}:")
                BaseGame.print_results(resultado, show_round_number=True, compact=True)
        else:
            BaseGame.print_results(results, show_round_number=True, compact=True)