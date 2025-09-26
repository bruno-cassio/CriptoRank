# CriptoRank - Web Scraping de Criptomoedas

Este projeto implementa um script Python para coleta de dados de criptomoedas diretamente da homepage do CoinGecko utilizando **Selenium** e  **BeautifulSoup** . O script gera um arquivo CSV padronizado com informações de preço, capitalização de mercado, volume e variações percentuais, compatível com o mesmo padrão da API.

## Estrutura do Projeto


Bruno_de_Cassio/

│

├─ outputs/                   # Diretório de saída de arquivos CSV

│  └─ top10_coins.csv         # Arquivo gerado pelo script

│

├─ scrape_coins.py            # Script principal de scraping

└─ README.md                  # Este arquivo


* `outputs`: Diretório dedicado à saída dos CSVs. Criado automaticamente pelo script se não existir.
* `scrape_coins.py`: Script principal com automação do navegador, extração de dados via HTML, tratamento de dados e salvamento do CSV.

## Instalação

1. Crie um ambiente virtual:

   `python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows`
2. Instale as dependências:

`pip install -r requirements.txt`

**Observação:** É necessário ter o navegador  **Chrome instalado** . O `webdriver-manager` fará o download automático do ChromeDriver compatível.

## Execução

`python scrape_coins.py`

## Decisões técnicas

1. **Automação segura com Selenium + WebDriver Manager**
   O script inicializa o Chrome via Selenium com tamanho de janela padrão, garantindo que todos os elementos carreguem corretamente. O WebDriver Manager garante compatibilidade automática do driver.
2. **Tratamento robusto de dados**
   * Conversão de valores monetários e percentuais com casas decimais padronizadas (`6 casas para valores, 2 casas para percentuais`).
   * Padronização de IDs, nomes e símbolos de moedas compatível com o padrão da API.
   * Garantia de ordem fixa de colunas e renomeação para cabeçalhos legíveis.
3. **Uso de BeautifulSoup para parsing eficiente**
   * Permite extrair dados da tabela de criptomoedas de forma resiliente, mesmo que a estrutura HTML contenha wrappers adicionais.
   * Evita dependência de parsers lentos ou fragilidade de regex.
4. **Logging e feedback ao usuário**
   * Mensagens informativas sobre acesso ao site, erros de scraping e sucesso no salvamento do CSV.
   * Facilita debugging em caso de mudanças na página ou falhas na rede.
5. **Criação automática da pasta de saída**
   * Garante que os arquivos CSV sejam salvos mesmo que a pasta `outputs` não exista, evitando erros de IO.
6. **Compatibilidade com API existente**
   * Estrutura de dados e cabeçalhos padronizados para fácil comparação com os dados obtidos via API CoinGecko.
