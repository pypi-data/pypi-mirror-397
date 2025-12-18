from .client import LoginClient
from .base_game import BaseGame, _LoginClientWrapper
from .game_factory import GameMethodFactory
import types

class Games(BaseGame):
    def __init__(self, client: LoginClient):
        if not isinstance(client, LoginClient):
            raise TypeError("Games só aceita LoginClient como parâmetro")
        
        client_wrapper = _LoginClientWrapper(client)
        super().__init__(client_wrapper)
        
        self._auto_translate = True
        self._custom_field_mapping = {}
        
        self._init_definitions()
        
        GameMethodFactory.inject_methods(self)
        
    def _init_definitions(self):
        self.ROULETTE_BASIC = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        self.ROULETTE_MEGA = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        self.ROULETTE_POWERUP = ["gameResult", "powerUpList", "powerUpMultipliers", "resultMultiplier", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        self.ROULETTE_FORTUNE = ["gameResult", "powerUpThresholdReached", "frWinType", "frMul", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        self.ROULETTE_PRIVATE = ["gameResult", "privateRoulette"]
        self.BACCARAT_STANDARD = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        self.BACCARAT_FORTUNE6 = ["playerHand", "bankerHand", "result", "fortune6"]
        self.BACCARAT_SUPER8 = ["playerHand", "bankerHand", "result", "super8"]
        self.BACCARAT_MEGA = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards", "d1", "d2", "sum", "mr", "mul"]
        self.SWEET_BONANZA = ["gameResult", "multiplier", "payout", "sugarbomb", "rc", "sbmul"]
        self.SPIN_24D = ["resultDesc", "winningNumber", "color", "even", "red"]
        self.SIC_BO = ["die1", "die2", "die3", "megaWinFlag", "maxMegaMul"]
        self.MEGA_SIC_BAC = ["firstDouble", "secondDouble", "triple", "quad", "result", "p1", "p2", "b1", "b2"]
        self.FOOTBALL_BLITZ = ["gameResult", "desc", "result", "cardDiff"]
        self.MONEY_TIME = ["gameResult", "multiplierValue", "boosterMultiplier"]
        self.DICE_CITY = ["gameResult", "rc", "boosterMul"]
        self.MEGA_WHEEL = ["gameResult", "multiplier", "jackpotwheel", "rngSlot"]
        self.TREASURE_ISLAND = ["gameResult", "rc", "betCodePayoffMap", "boosterMul", "payoutMul", "finalMul", "boosterWin", "bingoBallCount", "minMul", "maxMul", "blmDiceTotal", "bonusGame"]
        self.DRAGON_TIGER = ["gameResult", "desc"]
        self.ANDAR_BAHAR = ["result", "desc", "jokerScore", "cardValue", "andharCount", "baharCount", "jockerCount"]
        self.SPACEMAN = ["gameResult"]
    
    def get_available_games(self):
        return [f"get_{game}" for game in GameMethodFactory.GAMES_CONFIG.keys()]
    
    def get_game_info(self, game_name: str):
        return GameMethodFactory.GAMES_CONFIG.get(game_name)
    
    def __getattr__(self, name):
        if name.startswith('get_'):
            game_name = name[4:]
            if game_name in GameMethodFactory.GAMES_CONFIG:
                config = GameMethodFactory.GAMES_CONFIG[game_name]
                method = GameMethodFactory.create_game_method(game_name, config)
                setattr(self, name, method.__get__(self, type(self)))
                return getattr(self, name)
        
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'") 
   
    def enable_auto_translate(self):
        self._auto_translate = True
    
    def disable_auto_translate(self):
        self._auto_translate = False
    
    def is_auto_translate_enabled(self):
        return self._auto_translate
   
    def translate_fields(self, results, translate=None, custom_mapping=None):
        if translate is None:
            translate = self._auto_translate
        
        if not translate:
            return results
        
        default_field_mapping = {
            "BankerCards": "Cartas da Banca",
            "playerCards": "Cartas do Jogador",
            "playerHand": "Mão do Jogador",
            "bankerHand": "Mão da Banca",
            "playerScore": "Pontuação do Jogador",
            "winningScore": "Pontuação Vencedora",
            "desc": "Descrição",
            "result": "Resultado",
            "fortune6": "6 da Fortuna",
            "super8": "Super 8",
            "firstDouble": "Primeiro Par",
            "secondDouble": "Segundo Par",
            "triple": "Triplo",
            "quad": "Quadra",
            "p1": "Jogador 1",
            "p2": "Jogador 2",
            "b1": "Banca 1",
            "b2": "Banca 2",
            "d1": "Dado 1",
            "d2": "Dado 2",
            "sum": "Soma dos Dados",
            "mr": "Mega Resultado",
            "mul": "Multiplicador",
            "die1": "Dado 1",
            "die2": "Dado 2",
            "die3": "Dado 3",
            "megaWinFlag": "Mega Vitória",
            "maxMegaMul": "Multiplicador Máximo",
            "gameResult": "Resultado do Jogo",
            "powerUpThresholdReached": "PowerUp Atingido",
            "fortuneRoulette": "Fortune Roulette",
            "powerUpRoulette": "PowerUp Roulette",
            "megaRoulette": "Mega Roulette",
            "megaSlots": "Mega Slots",
            "megaPayouts": "Mega Pagamentos",
            "powerUpList": "Lista PowerUp",
            "powerUpMultipliers": "Multiplicadores PowerUp",
            "resultMultiplier": "Multiplicador do Resultado",
            "privateRoulette": "Roleta Privada",
            "frWinType": "Tipo de Vitória Fortune",
            "frMul": "Multiplicador Fortune",
            "resultDesc": "Descrição do Resultado",
            "winningNumber": "Número Vencedor",
            "color": "Cor",
            "even": "Par",
            "red": "Vermelho",
            "andharCount": "Contagem Andhar",
            "baharCount": "Contagem Bahar",
            "jockerCount": "Contagem Coringa",
            "jokerScore": "Pontuação do Coringa",
            "cardValue": "Valor da Carta",
            "cardDiff": "Diferença das Cartas",
            "multiplier": "Multiplicador",
            "payout": "Pagamento",
            "sugarbomb": "Sugar Bomb",
            "rc": "Código do Resultado",
            "sbmul": "Multiplicador SB",
            "multiplierValue": "Valor do Multiplicador",
            "boosterMultiplier": "Multiplicador Boost",
            "boosterMul": "Multiplicador Boost",
            "jackpotwheel": "Roda do Jackpot",
            "rngSlot": "Slot RNG",
            "betCodePayoffMap": "Mapa de Pagamentos",
            "payoutMul": "Multiplicador de Pagamento",
            "finalMul": "Multiplicador Final",
            "boosterWin": "Vitória Boost",
            "bingoBallCount": "Contagem de Bolas Bingo",
            "minMul": "Multiplicador Mínimo",
            "maxMul": "Multiplicador Máximo",
            "blmDiceTotal": "Total dos Dados BLM",
            "bonusGame": "Jogo Bônus",
            "Rodada": "Rodada"
        }
        
        field_mapping = default_field_mapping.copy()
        
        if hasattr(self, '_custom_field_mapping'):
            field_mapping.update(self._custom_field_mapping)
        
        if custom_mapping:
            field_mapping.update(custom_mapping)
        
        if isinstance(results, types.GeneratorType):
            def translate_generator():
                for resultado in results:
                    yield self._translate_result_list(resultado, field_mapping)
            return translate_generator()
        else:
            return self._translate_result_list(results, field_mapping)
    
    def _translate_result_list(self, result_list, field_mapping):
        if not isinstance(result_list, list):
            return result_list
        
        translated_results = []
        for result in result_list:
            translated_result = {}
            for key, value in result.items():
                translated_key = field_mapping.get(key, key)
                translated_result[translated_key] = value
            translated_results.append(translated_result)
        
        return translated_results
    
    def set_custom_field_names(self, field_mapping):
        if not hasattr(self, '_custom_field_mapping'):
            self._custom_field_mapping = {}
        self._custom_field_mapping.update(field_mapping)
    
    def get_custom_field_names(self):
        return getattr(self, '_custom_field_mapping', {})
    
    def clear_custom_field_names(self):
        self._custom_field_mapping = {}
    
    def print_json(self, results, custom_mapping=None):
        translated = self.translate_fields(results, custom_mapping=custom_mapping)
        super().print_json(translated)
    
    def print_compact(self, results, custom_mapping=None):
        translated = self.translate_fields(results, custom_mapping=custom_mapping)
        super().print_compact(translated)
    
    def print_results(self, results, show_round_number=True, compact=False, custom_mapping=None):
        translated = self.translate_fields(results, custom_mapping=custom_mapping)
        super().print_results(translated, show_round_number, compact)