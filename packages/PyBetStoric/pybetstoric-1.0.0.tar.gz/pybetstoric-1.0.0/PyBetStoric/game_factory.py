from typing import Dict, Any, Callable

class GameMethodFactory:
    GAMES_CONFIG = {
        "24d_spin": {
            "table_id": "24dspin000000001",
            "fields": "SPIN_24D"
        },
        "american_roulette": {
            "table_id": "americanroule296",
            "fields": "ROULETTE_BASIC"
        },
        "andar_bahar": {
            "table_id": "jzbzy021lg8xy9i2",
            "fields": "ANDAR_BAHAR"
        },
        "auto_mega_roulette": {
            "table_id": "1hl323e1lxuqdrkr",
            "fields": "ROULETTE_MEGA"
        },
        "auto_roulette": {
            "table_id": "5bzl2835s5ruvweg",
            "fields": "ROULETTE_BASIC"
        },
        "baccarat_1": {
            "table_id": "h22z8qhp17sa0vkh",
            "fields": "BACCARAT_STANDARD"
        },
        "baccarat_2": {
            "table_id": "9j3eagurfwmml7z2",
            "fields": "BACCARAT_STANDARD"
        },
        "baccarat_5": {
            "table_id": "ne074fgn4bd1150i",
            "fields": "BACCARAT_STANDARD"
        },
        "baccarat_6": {
            "table_id": "oq808ojps709qqaf",
            "fields": "BACCARAT_STANDARD"
        },
        "baccarat_7": {
            "table_id": "bcpirpmfpeobc191",
            "fields": "BACCARAT_STANDARD"
        },
        "baccarat_9": {
            "table_id": "bcpirpmfpobc1912",
            "fields": "BACCARAT_STANDARD"
        },
        "baccarat_brasileiro_1": {
            "table_id": "cbcf6qas8fscb222",
            "fields": "BACCARAT_STANDARD"
        },
        "brasileira_mega_roleta": {
            "table_id": "mrbras531mrbr532",
            "fields": "ROULETTE_MEGA"
        },
        "brasileira_roleta": {
            "table_id": "rwbrzportrwa16rg",
            "fields": "ROULETTE_BASIC"
        },
        "chinese_speed_baccarat_1": {
            "table_id": "spijbnsu408vmv71",
            "fields": "BACCARAT_STANDARD"
        },
        "chinese_speed_baccarat_2": {
            "table_id": "spijbnsu408vmv72",
            "fields": "BACCARAT_STANDARD"
        },
        "dice_city": {
            "table_id": "boomorbustccny01",
            "fields": "DICE_CITY"
        },
        "dragon_tiger": {
            "table_id": "drag0ntig3rsta48",
            "fields": "DRAGON_TIGER"
        },
        "football_blitz_top_card": {
            "table_id": "ge49e4os88bp4bi6",
            "fields": "FOOTBALL_BLITZ"
        },
        "fortune_6_baccarat": {
            "table_id": "bcpirpmfpobc1910",
            "fields": "BACCARAT_FORTUNE6"
        },
        "fortune_roulette": {
            "table_id": "megaroulettbba91",
            "fields": "ROULETTE_FORTUNE"
        },
        "french_roulette_la_partage": {
            "table_id": "frenchroulette01",
            "fields": "ROULETTE_BASIC"
        },
        "german_roulette": {
            "table_id": "s2x6b4jdeqza2ge2",
            "fields": "ROULETTE_BASIC"
        },
        "immersive_roulette_deluxe": {
            "table_id": "25irclas25imrcrw",
            "fields": "ROULETTE_POWERUP"
        },
        "indonesian_mega_sic_bo": {
            "table_id": "megasicboauto001",
            "fields": "SIC_BO"
        },
        "indonesian_speed_baccarat_1": {
            "table_id": "speedbca18generi",
            "fields": "BACCARAT_STANDARD"
        },
        "japonese_speed_baccarat_1": {
            "table_id": "spto41bctorobc41",
            "fields": "BACCARAT_STANDARD"
        },
        "japonese_speed_baccarat_2": {
            "table_id": "spto42bctorobc42",
            "fields": "BACCARAT_STANDARD"
        },
        "japonese_speed_baccarat_3": {
            "table_id": "spto43bctorobc43",
            "fields": "BACCARAT_STANDARD"
        },
        "korean_baccarat_1": {
            "table_id": "tobc52koreanto52",
            "fields": "BACCARAT_STANDARD"
        },
        "korean_roulette": {
            "table_id": "381rwkr381korean",
            "fields": "ROULETTE_BASIC"
        },
        "korean_speed_baccarat_1": {
            "table_id": "bc281koreanch281",
            "fields": "BACCARAT_STANDARD"
        },
        "korean_speed_baccarat_2": {
            "table_id": "bc392chromabc392",
            "fields": "BACCARAT_STANDARD"
        },
        "korean_speed_baccarat_3": {
            "table_id": "tobc51koreanto51",
            "fields": "BACCARAT_STANDARD"
        },
        "korean_speed_baccarat_5": {
            "table_id": "tobcspbaccarat61",
            "fields": "BACCARAT_STANDARD"
        },
        "lucky_6_roulette": {
            "table_id": "lucky6roulettea3",
            "fields": "ROULETTE_MEGA"
        },
        "mega_baccarat": {
            "table_id": "mbc371rpmfmbc371",
            "fields": "BACCARAT_MEGA"
        },
        "mega_roulette": {
            "table_id": "1hl65ce1lxuqdrkr",
            "fields": "ROULETTE_MEGA"
        },
        "mega_roulette_3000": {
            "table_id": "megaroulette3k01",
            "fields": "ROULETTE_MEGA"
        },
        "mega_sic_bac": {
            "table_id": "a10megasicbaca10",
            "fields": "MEGA_SIC_BAC"
        },
        "mega_wheel": {
            "table_id": "md500q83g7cdefw1",
            "fields": "MEGA_WHEEL"
        },
        "money_time": {
            "table_id": "moneytime2500002",
            "fields": "MONEY_TIME"
        },
        "powerup_roulette": {
            "table_id": "powruprw1qm3xc25",
            "fields": "ROULETTE_POWERUP"
        },
        "prive_lounge_baccarat_1": {
            "table_id": "privbca51privbc1",
            "fields": "BACCARAT_STANDARD"
        },
        "prive_lounge_baccarat_2": {
            "table_id": "privbca52privbc2",
            "fields": "BACCARAT_STANDARD"
        },
        "prive_lounge_baccarat_3": {
            "table_id": "privbca53privbc3",
            "fields": "BACCARAT_STANDARD"
        },
        "prive_lounge_baccarat_5": {
            "table_id": "privbca55privbc5",
            "fields": "BACCARAT_STANDARD"
        },
        "prive_lounge_roulette": {
            "table_id": "privroulettegt01",
            "fields": "ROULETTE_PRIVATE"
        },
        "prive_lounge_roulette_deluxe": {
            "table_id": "privroudeluxgt01",
            "fields": "ROULETTE_PRIVATE"
        },
        "roumanian_roulette": {
            "table_id": "romania233rwl291",
            "fields": "ROULETTE_BASIC"
        },
        "roulette_1": {
            "table_id": "g03y1t9vvuhrfytl",
            "fields": "ROULETTE_BASIC"
        },
        "roulette_2_extra_time": {
            "table_id": "5kvxlw4c1qm3xcyn",
            "fields": "ROULETTE_BASIC"
        },
        "roulette_3": {
            "table_id": "chroma229rwltr22",
            "fields": "ROULETTE_BASIC"
        },
        "roulette_italia_tricolore": {
            "table_id": "v1c52fgw7yy02upz",
            "fields": "ROULETTE_BASIC"
        },
        "roulette_latina": {
            "table_id": "roulerw234rwl292",
            "fields": "ROULETTE_BASIC"
        },
        "roullete_macao": {
            "table_id": "yqpz3ichst2xg439",
            "fields": "ROULETTE_BASIC"
        },
        "russian_roulette": {
            "table_id": "t4jzencinod6iqwi",
            "fields": "ROULETTE_BASIC"
        },
        "sic_bo": {
            "table_id": "sba71kkmr2ssba71",
            "fields": "SIC_BO"
        },
        "spaceman": {
            "table_id": "spacemanyxe123nh",
            "fields": "SPACEMAN"
        },
        "speed_auto_roulette": {
            "table_id": "autorwra311autor",
            "fields": "ROULETTE_BASIC"
        },
        "speed_baccarat_1": {
            "table_id": "pwnhicogrzeodk79",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_2": {
            "table_id": "kkqnazmd8ttq7fgd",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_3": {
            "table_id": "s8s9f0quk3ygiyb1",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_5": {
            "table_id": "886ewimul28yw14j",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_6": {
            "table_id": "2q57e43m4ivqwaq3",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_7": {
            "table_id": "bcpirpmfpeobc197",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_8": {
            "table_id": "bcpirpmfpeobc198",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_9": {
            "table_id": "bcpirpmfpeobc196",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_10": {
            "table_id": "bcpirpmfpeobc194",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_16": {
            "table_id": "bcpirpmfpobc1911",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_17": {
            "table_id": "bcpirpmfpebc1908",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_18": {
            "table_id": "b0jf7rlboleibnap",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_brasileiro_1": {
            "table_id": "bcpirpmfpeobc193",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_brasileiro_2": {
            "table_id": "m88hicogrzeod202",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_brasileiro_3": {
            "table_id": "cbcf6qas8fscb221",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_baccarat_brasileiro_4": {
            "table_id": "cbcf6qas8fscb224",
            "fields": "BACCARAT_STANDARD"
        },
        "speed_roulette_1": {
            "table_id": "fl9knouu0yjez2wi",
            "fields": "ROULETTE_BASIC"
        },
        "speed_roulette_2": {
            "table_id": "r20speedrtwo201s",
            "fields": "ROULETTE_BASIC"
        },
        "speed_roulette_latina": {
            "table_id": "cosproulttf8s6sr",
            "fields": "ROULETTE_BASIC"
        },
        "squeeze_baccarat": {
            "table_id": "bcadigitalsqz001",
            "fields": "BACCARAT_STANDARD"
        },
        "super_8_baccarat": {
            "table_id": "bcpirpmfpeobc199",
            "fields": "BACCARAT_SUPER8"
        },
        "sweet_bonanza_candyland": {
            "table_id": "pbvzrfk1fyft4dwe",
            "fields": "SWEET_BONANZA"
        },
        "thai_roulette": {
            "table_id": "thairwa13generw1",
            "fields": "ROULETTE_BASIC"
        },
        "thai_speed_baccarat_1": {
            "table_id": "speedbca14gesbc1",
            "fields": "BACCARAT_STANDARD"
        },
        "thai_speed_baccarat_2": {
            "table_id": "speedbca14gesbc2",
            "fields": "BACCARAT_STANDARD"
        },
        "treasure_island": {
            "table_id": "treasureadvgt001",
            "fields": "TREASURE_ISLAND"
        },
        "turbo_baccarat_brasileiro_1": {
            "table_id": "bcpirpmfpeobc192",
            "fields": "BACCARAT_STANDARD"
        },
        "turkish_mega_roulette": {
            "table_id": "megar0ul3tt3trk1",
            "fields": "ROULETTE_MEGA"
        },
        "turkish_roulette": {
            "table_id": "p8l1j84prrmxzyic",
            "fields": "ROULETTE_BASIC"
        },
        "viatnamese_speed_baccarat_1": {
            "table_id": "spto11bctorobc11",
            "fields": "BACCARAT_STANDARD"
        },
        "viatnamese_speed_baccarat_2": {
            "table_id": "spto12bctorobc12",
            "fields": "BACCARAT_STANDARD"
        },
        "viatnamese_speed_baccarat_3": {
            "table_id": "spto21bctorobc21",
            "fields": "BACCARAT_STANDARD"
        },
        "vietnamese_roulette": {
            "table_id": "vietnamr32genric",
            "fields": "ROULETTE_BASIC"
        },
        "vip_auto_roulette": {
            "table_id": "ar25vipautorw251",
            "fields": "ROULETTE_BASIC"
        },
        "vip_roulette": {
            "table_id": "geogamingh2rw545",
            "fields": "ROULETTE_BASIC"
        },
    }
    
    @classmethod
    def create_game_method(cls, game_name: str, config: Dict[str, str]) -> Callable:
        table_id = config["table_id"]
        fields_attr = config["fields"]
        
        def game_method(self, number_of_games=None, repeat=None, interval=None):
            def _execute():
                fields = getattr(self, fields_attr)
                return self._get_game_history(
                    table_id, 
                    fields, 
                    number_of_games or self.NUMBER_OF_GAMES
                )
            return self._execute_with_repeat(_execute, repeat, interval)
        
        game_method.__name__ = f"get_{game_name}"
        return game_method
    
    @classmethod
    def inject_methods(cls, game_instance) -> None:
        for game_name, config in cls.GAMES_CONFIG.items():
            method_name = f"get_{game_name}"
            method = cls.create_game_method(game_name, config)
            setattr(game_instance, method_name, method.__get__(game_instance, type(game_instance)))