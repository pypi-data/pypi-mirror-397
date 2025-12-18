# 📚 PyBetStoric - Documentação Completa

## 📋 Índice
- [Visão Geral](#visão-geral)
- [Instalação](#instalação)
- [Início Rápido](#início-rápido)
- [Autenticação](#autenticação)
- [Jogos Disponíveis](#jogos-disponíveis)
- [Métodos Principais](#métodos-principais)
- [Configurações](#configurações)
- [Formatos de Exibição](#formatos-de-exibição)
- [Recursos Avançados](#recursos-avançados)
- [Exemplos Práticos](#exemplos-práticos)
- [Tratamento de Erros](#tratamento-de-erros)

---

## 🎯 Visão Geral

**PyBetStoric** é uma biblioteca Python para obter históricos de jogos de cassino ao vivo. A biblioteca oferece acesso programático a dados de mais de 95 jogos diferentes, incluindo Baccarat, Roleta, Sic Bo e Game Shows.

### Características Principais:
- ✅ **95+ Jogos Suportados**: Baccarat, Roleta, Sic Bo, Game Shows e mais
- ✅ **Autenticação Segura**: Sistema de licenças com cache de sessão
- ✅ **Múltiplos Formatos**: JSON, Compacto, Detalhado
- ✅ **Tradução Automática**: Campos em português
- ✅ **Execução Repetida**: Coleta contínua de dados
- ✅ **Cache Inteligente**: Otimização de performance

---

## 🚀 Instalação

### Pré-requisitos
```bash
pip install PyBetStoric
```

### Instalação da Biblioteca
```python
import PyBetStoric
```

---

## ⚡ Início Rápido

```python
import PyBetStoric

# 1. Autenticação
client = PyBetStoric.LoginClient(
    email="seu_email@exemplo.com",
    user="seu_usuario",
    password="sua_senha",
    license_code="SEU_CODIGO_LICENCA"
)

# 2. Inicializar Games
games = PyBetStoric.Games(client)

# 3. Obter dados
resultados = games.get_baccarat_1(number_of_games=20)

# 4. Exibir resultados
games.print_results(resultados)

# 5. Fechar conexão
client.close()
```

---

## 🔐 Autenticação

### LoginClient

O `LoginClient` é responsável pela autenticação e gerenciamento de sessão.

```python
client = PyBetStoric.LoginClient(
    email="email@exemplo.com",      # Email cadastrado
    user="usuario123",              # Nome de usuário
    password="senha123",            # Senha da conta
    license_code="ABC123XYZ"        # Código de licença
)
```

### Métodos do Client

| Método | Descrição | Retorno |
|--------|-----------|---------|
| `get_history(table_id, number_of_games)` | Obter histórico direto | `dict` |
| `get_jsessionid()` | Obter ID da sessão | `string` |
| `is_authenticated()` | Verificar autenticação | `boolean` |
| `close()` | Fechar conexão | `None` |

### Exemplo de Uso:
```python
# Verificar autenticação
if client.is_authenticated():
    print("Cliente autenticado com sucesso!")

# Obter histórico direto
history = client.get_history("h22z8qhp17sa0vkh", 10)
print(f"Jogos obtidos: {len(history['history'])}")
```

---

## 🎮 Jogos Disponíveis

### Categorias de Jogos

#### 🎰 Roletas (25+ variações)
- **Básicas**: American, Auto, German, Russian
- **Regionais**: Brazilian, Korean, Thai, Turkish, Vietnamese
- **Especiais**: Mega, PowerUp, Fortune, Lucky 6
- **VIP**: Private Lounge, VIP Auto, VIP Standard

#### 🃏 Baccarat (30+ mesas)
- **Padrão**: Baccarat 1-9, Brazilian Baccarat
- **Speed**: Speed Baccarat 1-18, Regional Speed
- **Especiais**: Mega, Fortune 6, Super 8, Squeeze
- **Privadas**: Private Lounge 1-5

#### 🎲 Sic Bo
- **Tradicional**: Sic Bo padrão
- **Mega**: Indonesian Mega Sic Bo
- **Híbrido**: Mega Sic Bac

#### 🎪 Game Shows
- **Sweet Bonanza Candyland**: Jogo temático de doces
- **Money Time**: Multiplicadores de dinheiro
- **Mega Wheel**: Roda da fortuna
- **Treasure Island**: Caça ao tesouro
- **Dice City**: Jogo urbano de dados
- **Football Blitz**: Temático de futebol
- **Spaceman**: Multiplicador espacial

#### 🎯 Outros Jogos
- **Dragon Tiger**: Comparação simples de cartas
- **Andar Bahar**: Jogo indiano tradicional
- **24D Spin**: Jogo de spin com 24 posições

### Lista Completa de Métodos

```python
# Obter lista de todos os jogos
jogos_disponiveis = games.get_available_games()
print(f"Total: {len(jogos_disponiveis)} jogos")

# Obter informações de um jogo específico
info = games.get_game_info("baccarat_1")
print(f"Table ID: {info['table_id']}")
print(f"Campos: {info['fields']}")
```

---

## 🛠️ Métodos Principais

### Classe Games

A classe `Games` é o ponto principal para obter dados dos jogos.

```python
games = PyBetStoric.Games(client)
```

### Padrão de Métodos

Todos os jogos seguem o mesmo padrão:

```python
# Sintaxe geral
resultados = games.get_NOME_DO_JOGO(
    number_of_games=100,    # Quantidade (1-500)
    repeat=1,               # Repetições (1, 5, "i" para infinito)
    interval=None           # Intervalo em segundos
)
```

### Exemplos por Categoria:

#### Baccarat
```python
# Baccarat básico
baccarat_1 = games.get_baccarat_1(number_of_games=20)
baccarat_2 = games.get_baccarat_2(number_of_games=30)

# Speed Baccarat
speed_baccarat_1 = games.get_speed_baccarat_1(number_of_games=25)
speed_baccarat_brasileiro_1 = games.get_speed_baccarat_brasileiro_1(number_of_games=40)

# Baccarat especial
mega_baccarat = games.get_mega_baccarat(number_of_games=15)
fortune_6_baccarat = games.get_fortune_6_baccarat(number_of_games=35)
```

#### Roleta
```python
# Roletas básicas
american_roulette = games.get_american_roulette(number_of_games=30)
auto_roulette = games.get_auto_roulette(number_of_games=25)

# Roletas especiais
mega_roulette = games.get_mega_roulette(number_of_games=40)
powerup_roulette = games.get_powerup_roulette(number_of_games=20)

# Roletas regionais
brasileira_roleta = games.get_brasileira_roleta(number_of_games=35)
korean_roulette = games.get_korean_roulette(number_of_games=30)
```

#### Game Shows
```python
# Game Shows populares
sweet_bonanza = games.get_sweet_bonanza_candyland(number_of_games=15)
money_time = games.get_money_time(number_of_games=20)
mega_wheel = games.get_mega_wheel(number_of_games=25)
treasure_island = games.get_treasure_island(number_of_games=30)
```

---

## ⚙️ Configurações

### Sistema de Tradução

#### Controle da Tradução Automática
```python
# Verificar status
status = games.is_auto_translate_enabled()
print(f"Tradução habilitada: {status}")

# Habilitar tradução
games.enable_auto_translate()

# Desabilitar tradução
games.disable_auto_translate()
```

#### Campos Personalizados
```python
# Definir campos personalizados
mapeamento_custom = {
    "desc": "Resultado Final",
    "playerScore": "Pontos Jogador",
    "winningScore": "Pontos Vencedor",
    "playerCards": "Cartas do Jogador",
    "BankerCards": "Cartas da Banca"
}

games.set_custom_field_names(mapeamento_custom)

# Obter mapeamento atual
campos_atuais = games.get_custom_field_names()

# Limpar campos personalizados
games.clear_custom_field_names()
```

#### Tradução Manual
```python
# Traduzir com configuração padrão
traduzido = games.translate_fields(resultados, translate=True)

# Traduzir com mapeamento personalizado
traduzido_custom = games.translate_fields(
    resultados, 
    translate=True, 
    custom_mapping={"desc": "RESULTADO"}
)

# Sem tradução
sem_traducao = games.translate_fields(resultados, translate=False)
```

---

## 📊 Formatos de Exibição

### 1. Formato JSON
Ideal para APIs e processamento de dados:

```python
games.print_json(resultados)
```

**Saída:**
```json
[
{"Descrição": "Player", "Pontuação do Jogador": 7, "Pontuação Vencedora": 7, "Cartas do Jogador": ["4D", "3D"], "Cartas da Banca": null, "Rodada": 1},
{"Descrição": "Banker", "Pontuação do Jogador": 4, "Pontuação Vencedora": 5, "Cartas do Jogador": ["3C", "2H"], "Cartas da Banca": null, "Rodada": 2}
]
```

### 2. Formato Compacto
Uma linha por resultado:

```python
games.print_compact(resultados)
```

**Saída:**
```
Rodada  1: Descrição: Player | Pontuação do Jogador: 7 | Pontuação Vencedora: 7
Rodada  2: Descrição: Banker | Pontuação do Jogador: 4 | Pontuação Vencedora: 5
```

### 3. Formato Detalhado
Formato completo com todos os campos:

```python
# Com número da rodada
games.print_results(resultados, show_round_number=True, compact=False)

# Sem número da rodada
games.print_results(resultados, show_round_number=False, compact=False)
```

**Saída:**
```
RODADA 1:
   Descrição: Player
   Pontuação do Jogador: 7
   Pontuação Vencedora: 7
   Cartas do Jogador: ['4D', '3D']
   Cartas da Banca: None
```

### 4. Formatação Personalizada
```python
# Com tradução personalizada
games.print_json(resultados, custom_mapping={"desc": "RESULTADO"})
games.print_compact(resultados, custom_mapping={"playerScore": "PONTOS"})
games.print_results(resultados, custom_mapping={"winningScore": "VENCEDOR"})
```

---

## 🚀 Recursos Avançados

### Execução com Repetição

#### Repetição Finita
```python
# Executar 5 vezes com intervalo de 10 segundos
resultados = games.get_baccarat_1(
    number_of_games=20,
    repeat=5,
    interval=10
)

# Processar resultados
for i, resultado in enumerate(resultados, 1):
    print(f"Execução {i}: {len(resultado)} jogos")
```

#### Execução Infinita
```python
# Executar infinitamente até interrupção (Ctrl+C)
resultados_infinitos = games.get_baccarat_1(
    number_of_games=10,
    repeat="i",
    interval=30  # A cada 30 segundos
)

# Processar em tempo real
try:
    for resultado in resultados_infinitos:
        print(f"Novos dados: {len(resultado)} jogos")
        # Processar dados aqui
except KeyboardInterrupt:
    print("Execução interrompida pelo usuário")
```

### Cache de Sessão

O sistema possui cache automático de sessão:

```python
# Cache é gerenciado automaticamente
# Arquivo: .DO_NOT_DELET.json
# Tempo de vida: 10 minutos

# Verificar se sessão está válida
if client.is_authenticated():
    print("Sessão ativa (pode ser do cache)")
```

### Análise de Dados

```python
# Obter dados para análise
dados = games.get_baccarat_1(number_of_games=100)

# Contar resultados
contadores = {}
for jogo in dados:
    resultado = jogo.get('Descrição', 'Desconhecido')
    contadores[resultado] = contadores.get(resultado, 0) + 1

# Calcular percentuais
total = len(dados)
for resultado, count in contadores.items():
    percentual = (count / total) * 100
    print(f"{resultado}: {count} ({percentual:.1f}%)")
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Monitoramento Básico
```python
import PyBetStoric

# Configuração
client = PyBetStoric.LoginClient(
    email="email@exemplo.com",
    user="usuario",
    password="senha",
    license_code="LICENCA"
)
games = PyBetStoric.Games(client)

# Obter últimos 50 resultados do Baccarat
resultados = games.get_baccarat_1(number_of_games=50)

# Exibir em formato compacto
games.print_compact(resultados)

client.close()
```

### Exemplo 2: Análise Estatística
```python
import PyBetStoric

client = PyBetStoric.LoginClient(
    email="email@exemplo.com",
    user="usuario", 
    password="senha",
    license_code="LICENCA"
)
games = PyBetStoric.Games(client)

# Coletar dados de múltiplas mesas
baccarat_1 = games.get_baccarat_1(number_of_games=100)
baccarat_2 = games.get_baccarat_2(number_of_games=100)
speed_baccarat = games.get_speed_baccarat_1(number_of_games=100)

# Análise comparativa
def analisar_resultados(dados, nome_mesa):
    contadores = {}
    for jogo in dados:
        resultado = jogo.get('Descrição', jogo.get('desc', 'N/A'))
        contadores[resultado] = contadores.get(resultado, 0) + 1
    
    print(f"\n=== {nome_mesa} ===")
    total = len(dados)
    for resultado, count in contadores.items():
        percentual = (count / total) * 100
        print(f"{resultado}: {count}/{total} ({percentual:.1f}%)")

analisar_resultados(baccarat_1, "Baccarat 1")
analisar_resultados(baccarat_2, "Baccarat 2") 
analisar_resultados(speed_baccarat, "Speed Baccarat 1")

client.close()
```

### Exemplo 3: Coleta Contínua
```python
import PyBetStoric
import time

client = PyBetStoric.LoginClient(
    email="email@exemplo.com",
    user="usuario",
    password="senha", 
    license_code="LICENCA"
)
games = PyBetStoric.Games(client)

# Configurar campos personalizados
games.set_custom_field_names({
    "desc": "Resultado",
    "playerScore": "Jogador",
    "winningScore": "Vencedor"
})

print("Iniciando coleta contínua... (Ctrl+C para parar)")

try:
    # Coleta a cada 60 segundos
    resultados_continuos = games.get_baccarat_1(
        number_of_games=5,
        repeat="i",
        interval=60
    )
    
    for i, resultado in enumerate(resultados_continuos, 1):
        print(f"\n--- Coleta {i} ({time.strftime('%H:%M:%S')}) ---")
        games.print_compact(resultado)
        
except KeyboardInterrupt:
    print("\nColeta interrompida pelo usuário")
finally:
    client.close()
```

### Exemplo 4: Múltiplos Jogos
```python
import PyBetStoric

client = PyBetStoric.LoginClient(
    email="email@exemplo.com",
    user="usuario",
    password="senha",
    license_code="LICENCA"
)
games = PyBetStoric.Games(client)

# Lista de jogos para monitorar
jogos_para_monitorar = [
    ("Baccarat 1", lambda: games.get_baccarat_1(number_of_games=20)),
    ("American Roulette", lambda: games.get_american_roulette(number_of_games=20)),
    ("Mega Wheel", lambda: games.get_mega_wheel(number_of_games=15)),
    ("Dragon Tiger", lambda: games.get_dragon_tiger(number_of_games=25))
]

# Coletar dados de todos os jogos
for nome_jogo, metodo_jogo in jogos_para_monitorar:
    print(f"\n{'='*50}")
    print(f"COLETANDO: {nome_jogo}")
    print(f"{'='*50}")
    
    try:
        dados = metodo_jogo()
        print(f"Dados coletados: {len(dados)} resultados")
        
        # Exibir últimos 3 resultados
        games.print_results(dados[:3], show_round_number=True, compact=True)
        
    except Exception as e:
        print(f"Erro ao coletar {nome_jogo}: {e}")

client.close()
```

---

## ⚠️ Tratamento de Erros

### Erros Comuns

#### 1. Erro de Autenticação
```python
try:
    client = PyBetStoric.LoginClient(
        email="email@exemplo.com",
        user="usuario",
        password="senha_incorreta",
        license_code="LICENCA"
    )
except Exception as e:
    print(f"Erro de autenticação: {e}")
```

#### 2. Erro de Licença
```python
try:
    client = PyBetStoric.LoginClient(
        email="email@exemplo.com",
        user="usuario", 
        password="senha",
        license_code="LICENCA_INVALIDA"
    )
except Exception as e:
    print(f"Erro de licença: {e}")
```

#### 3. Erro de Rede
```python
try:
    resultados = games.get_baccarat_1(number_of_games=50)
except Exception as e:
    print(f"Erro de rede: {e}")
    # Tentar novamente após alguns segundos
    time.sleep(5)
    resultados = games.get_baccarat_1(number_of_games=50)
```

### Boas Práticas

#### 1. Sempre Fechar Conexões
```python
client = None
try:
    client = PyBetStoric.LoginClient(...)
    games = PyBetStoric.Games(client)
    # Seu código aqui
finally:
    if client:
        client.close()
```

#### 2. Verificar Autenticação
```python
if not client.is_authenticated():
    print("Cliente não autenticado!")
    exit(1)
```

#### 3. Validar Parâmetros
```python
# Validar number_of_games
number_of_games = min(max(1, number_of_games), 500)

# Validar repeat e interval
if repeat > 1 and interval is None:
    raise ValueError("Interval é obrigatório quando repeat > 1")
```

---

## 📝 Campos de Dados

### Baccarat
| Campo Original | Tradução | Descrição |
|----------------|----------|-----------|
| `desc` | `Descrição` | Resultado (Player/Banker/Tie) |
| `playerScore` | `Pontuação do Jogador` | Pontos do jogador |
| `winningScore` | `Pontuação Vencedora` | Pontos vencedores |
| `playerCards` | `Cartas do Jogador` | Cartas do jogador |
| `BankerCards` | `Cartas da Banca` | Cartas da banca |

### Roleta
| Campo Original | Tradução | Descrição |
|----------------|----------|-----------|
| `gameResult` | `Resultado do Jogo` | Número vencedor |
| `powerUpThresholdReached` | `PowerUp Atingido` | PowerUp ativado |
| `fortuneRoulette` | `Fortune Roulette` | Resultado Fortune |
| `megaRoulette` | `Mega Roulette` | Multiplicador Mega |

### Sic Bo
| Campo Original | Tradução | Descrição |
|----------------|----------|-----------|
| `die1` | `Dado 1` | Valor do primeiro dado |
| `die2` | `Dado 2` | Valor do segundo dado |
| `die3` | `Dado 3` | Valor do terceiro dado |
| `megaWinFlag` | `Mega Vitória` | Flag de mega vitória |

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```python
import os

# Usar variáveis de ambiente para credenciais
client = PyBetStoric.LoginClient(
    email=os.getenv('PYBET_EMAIL'),
    user=os.getenv('PYBET_USER'),
    password=os.getenv('PYBET_PASSWORD'),
    license_code=os.getenv('PYBET_LICENSE')
)
```

### Logging Personalizado
```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pybet.log'),
        logging.StreamHandler()
    ]
)

# Usar no código
logger = logging.getLogger(__name__)

try:
    resultados = games.get_baccarat_1(number_of_games=50)
    logger.info(f"Coletados {len(resultados)} resultados")
except Exception as e:
    logger.error(f"Erro na coleta: {e}")
```

---

## 📊 Performance e Otimização

### Dicas de Performance

1. **Use cache de sessão**: Evite reautenticações desnecessárias
2. **Limite number_of_games**: Máximo recomendado: 100-200 por chamada
3. **Use intervalos adequados**: Mínimo 10 segundos entre chamadas
4. **Feche conexões**: Sempre use `client.close()`

### Monitoramento de Recursos
```python
import time
import psutil

def monitorar_performance():
    inicio = time.time()
    memoria_inicial = psutil.Process().memory_info().rss / 1024 / 1024
    
    # Seu código aqui
    resultados = games.get_baccarat_1(number_of_games=100)
    
    fim = time.time()
    memoria_final = psutil.Process().memory_info().rss / 1024 / 1024
    
    print(f"Tempo: {fim - inicio:.2f}s")
    print(f"Memória: {memoria_final - memoria_inicial:.2f}MB")
    print(f"Resultados: {len(resultados)}")
```

---

## 🆘 Suporte e Troubleshooting

### Problemas Comuns

#### 1. "Erro de autenticação"
- Verifique email, usuário e senha
- Confirme se a licença está ativa
- Tente limpar o cache: delete `.DO_NOT_DELET.json`

#### 2. "Sessão expirada"
- O sistema reautentica automaticamente
- Se persistir, reinicie o cliente

#### 3. "Erro de rede"
- Verifique conexão com internet
- Tente novamente após alguns segundos
- Verifique se não há firewall bloqueando

#### 4. "Dados vazios"
- Mesa pode estar offline
- Tente outra mesa similar
- Verifique se o table_id está correto

### Arquivos de Log
- `app.error`: Erros detalhados do sistema
- `.DO_NOT_DELET.json`: Cache de sessões

---

## 📄 Licença e Termos

Esta biblioteca requer uma licença válida para funcionamento. Entre em contato com o fornecedor para:
- Obter licença
- Renovar assinatura
- Suporte técnico
- Documentação adicional

---

## 🔄 Changelog

### Versão Atual
- ✅ 95+ jogos suportados
- ✅ Sistema de cache otimizado
- ✅ Tradução automática
- ✅ Múltiplos formatos de saída
- ✅ Execução com repetição
- ✅ Tratamento robusto de erros

---

**📞 Para suporte técnico ou dúvidas, consulte a documentação oficial ou entre em contato com o suporte.**