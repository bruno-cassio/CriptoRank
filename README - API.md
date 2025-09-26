# CriptoRank - Consumo API.

Projeto de coleta de dados de API e Webscrapy de dados de carteiras de Criptomoedas, dinamismo aplicado.

# Projeto de Coleta de Dados de Criptomoedas via API CoinGecko

Este projeto implementa um script Python para coleta de dados de criptomoedas usando a API pública do CoinGecko. O script gera um arquivo CSV padronizado com informações de preço, capitalização de mercado, volume e variações percentuais.

## Estrutura do Projeto

Bruno_de_Cassio/
│
├─ outputs/                  # Diretório de saída de arquivos CSV
│  └─ api_output.csv         # Arquivo gerado pelo script
│
├─ .env                      # Variáveis de configuração sensíveis e parametrizáveis
├─ crypto_api.py             # Script principal de coleta via API
└─ README.md                 # Este arquivo

* outputs: Diretório dedicado à saída dos CSVs. Criado automaticamente pelo script se não existir.
* .env: Centraliza todas as variáveis de configuração, permitindo alterações rápidas sem modificar o código.
* crypto_api.py: Script principal com coleta via API, tratamento de dados e salvamento do CSV.

## Instalação

1. Crie um ambiente virtual :

   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
2. Instale as dependências:

   pip install -r requirements.txt

## Boas práticas e decisões técnicas

1. Fail-fast para variáveis obrigatórias

   Todas as variáveis essenciais do .env são verificadas no início. Caso alguma não exista, o script levanta erro imediatamente, evitando execução parcial ou dados inconsistentes.
2. Uso de requests.Session

   Reaproveitamento de conexões HTTP para otimizar chamadas à API, reduzindo overhead e respeitando limites de rate.
3. Rate limit configurável

   Delay entre requisições parametrizado via .env para respeitar políticas da API e prevenir bloqueios.
4. Logging detalhado e configurável

   Logs em nível DEBUG para desenvolvimento e DEBUG/INFO para produção. Inclui parâmetros, status da API, quantidade de dados e DataFrame antes/depois da formatação.
5. Tratamento de dados e normalização

   Colunas fixas e padronizadas, funções auxiliares para conversão segura, e opção de saída em formato humano-legível ou numérico para processamento.
6. Criação automática da pasta de saída

   Garante que o CSV seja salvo sem falhas mesmo que o diretório não exista.
7. Timezone consistente

   Todas as datas seguem o timezone configurado no .env para evitar inconsistências em relatórios ou integrações.

## Exemplo de .env

API_URL=https://api.coingecko.com/api/v3/coins/markets
DEFAULT_CURRENCY=usd
DEFAULT_PER_PAGE=10
RATE_LIMIT_DELAY=1
TIMEZONE=America/Sao_Paulo
OUTPUT_FILE=Bruno_de_Cassio/outputs/api_output.csv

## Execução

python crypto_api.py
