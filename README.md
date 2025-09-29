CriptoRank - Coleta de Dados de Criptomoedas via API e Web Scraping

Projeto para coleta de dados das top 10 criptomoedas e exchanges via API CoinGecko e web scraping com Selenium/BeautifulSoup. O foco é em dados dinâmicos de mercado (preço, market cap, volume, variações percentuais), gerando CSVs padronizados para análise. 

Arquitetura
O projeto adota uma Arquitetura Modular Baseada em Serviços (Modular Service-Based Architecture), inspirada em princípios de Clean Architecture e Separation of Concerns. Essa escolha visa priorizar escalabilidade, testabilidade e manutenção, evitando código monolítico. 

Motivação: Em vez de scripts flat, separei responsabilidades em módulos independentes, facilitando expansão (ex: adicionar database ou UI) e alinhando à devolutiva. É simples para RPA, mas robusta para produção.

Estrutura:
Camadas:
Services: /src/api (para consumo de API) e /src/scraping (para web scraping) como "serviços" independentes, cada um com sua lógica de fetch/normalização.

Utils/Tools: /src/tools para funções reutilizáveis (ex: save_to_csv, parse_currency), compartilhadas entre API e scraping.
Data: /data para saídas (CSVs), separada do código.


Fluxo: Scripts modulares (crypto_api.py, scrape_coins.py) podem ser orquestrados por um main.py futuro. Dados crus são normalizados para consistência (ex: floats com 6 decimais, datas em GMT-3).
Vantagens: Independência (API não depende de scraping), fácil debugging (logs por módulo), e alinhamento a padrões como MVC adaptado (Models como dataclass futura, Controllers como services).



Estrutura do repositório:
Bruno_de_Cassio/
├── src/
│   ├── api/
│   │   └── crypto_api.py  # Coleta via API CoinGecko
│   ├── scraping/
│   │   └── scrape_coins.py  # Web scraping com Selenium/BS4
│   └── tools/
│       └── tools.py  # Funções auxiliares (ex: save_to_csv)
├── data/  # Saídas (CSVs gerados)
│   ├── api_output.csv
│   └── top10_coins.csv
├── .env  # Configs sensíveis (API_URL, TIMEZONE, etc.)
├── requirements.txt  # Dependências
└── README.md  # Documentação unificada

Tecnologias Usadas

Python
API: requests (para HTTP), pandas (para DataFrames), pytz (para timezones), python-dotenv (para .env)
Scraping: selenium (para navegador), webdriver-manager (para drivers), beautifulsoup4 (para parsing HTML), lxml (parser rápido)

Outros: logging (para logs), typing (para anotações), pathlib (para paths)

Instalação

Crie um ambiente virtual:
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


Instale as dependências:
python -m pip install -r requirements.txt


Observação: Para Selenium, o navegador Chrome é necessário. O webdriver-manager baixa o driver automaticamente.
Execução

Coleta via API:
python -m src.api.crypto_api


Output: /data/api_output.csv


Coleta via Web Scraping:
python -m src.scraping.scrape_coins


Output: /data/top10_coins.csv



Decisões Técnicas

Fail-fast para Variáveis Obrigatórias: Variáveis do .env são validadas no início para evitar execução parcial.

Uso de requests.Session: Reaproveitamento de conexões HTTP na API para otimizar chamadas e respeitar rate limits.

Rate Limit Configurável: Delays parametrizados no .env para prevenir bloqueios na API.

Logging Detalhado: Nível DEBUG/INFO com mensagens sobre params, erros e DataFrames antes/depois da formatação.

Tratamento e Normalização de Dados: Colunas fixas, funções auxiliares para conversão segura (ex: safe_float), e formatação opcional (U$/% ou numérico) via .env.

Criação Automática de Pastas: os.makedirs garante que /data exista, evitando erros de IO.

Timezone Consistente: Datas ajustadas para o timezone do .env (ex: America/Sao_Paulo).

Robustez no Scraping: Selenium com window-size fixo, espera para JS, e BeautifulSoup para parsing resiliente. Conversões padronizadas para compatibilidade com API.

Compatibilidade entre API e Scraping: Estrutura de dados e cabeçalhos idênticos para fácil comparação.


Exemplo de .env
API_URL=https://api.coingecko.com/api/v3/coins/markets
DEFAULT_CURRENCY=usd
DEFAULT_PER_PAGE=10
RATE_LIMIT_DELAY=1
TIMEZONE=America/Sao_Paulo
OUTPUT_FILE=Bruno_de_Cassio/data/api_output.csv

Resultado Esperado
CSVs com colunas como "ID Moeda", "Nome", "Preço (U$)", "Capitalização (U$)", etc., com dados das top 10 moedas. Exemplo de linha (BTC):

ID Moeda: bitcoin
Preço (U$): 109422.123456
Variação 24h (%): 3.876543
