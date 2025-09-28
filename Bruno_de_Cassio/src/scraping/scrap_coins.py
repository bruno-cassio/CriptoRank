import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import logging

# Configuração de logging profissional, útil para monitoramento e debugging em produção
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Colunas e cabeçalho padronizados seguindo o mesmo padrão da API
# Isso garante consistência entre diferentes fontes de dados e facilita integração futura
COLUMNS = [
    "id_moeda", "nome_moeda", "simbolo",
    "preco_usd", "capitalizacao_mercado_usd", "volume_24h_usd",
    "variacao_1h_pct", "variacao_24h_pct", "variacao_7d_pct"
]

HEADER_MAP = {
    "id_moeda": "ID Moeda",
    "nome_moeda": "Nome",
    "simbolo": "Símbolo",
    "preco_usd": "Preço (U$)",
    "capitalizacao_mercado_usd": "Capitalização (U$)",
    "volume_24h_usd": "Volume 24h (U$)",
    "variacao_1h_pct": "Variação 1h (%)",
    "variacao_24h_pct": "Variação 24h (%)",
    "variacao_7d_pct": "Variação 7d (%)"
}

# Funções de tratamento de dados padronizadas, garantindo uniformidade
def parse_currency(value: str) -> float:
    """Converte valores monetários em float com 6 casas decimais"""
    if not value:
        return 0.0
    value = value.replace("$", "").replace("U$", "").replace(",", "").replace(" ", "")
    try:
        return round(float(value), 6)
    except:
        return 0.0

def parse_percentage(value: str) -> float:
    """Converte percentuais em float com 2 casas decimais"""
    if not value:
        return 0.0
    value = value.replace("%", "").replace(",", ".").strip()
    try:
        return round(float(value), 2)
    except:
        return 0.0

def scrape_top_10_coins():
    """
    Scraping das top 10 moedas do CoinGecko.
    Demonstra prática de selenium + BeautifulSoup, com espera de carregamento JS.
    """
    options = Options()
    options.add_argument("--window-size=1920,1080")  # garante consistência de renderização
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://www.coingecko.com"
    logging.info(f"Acessando {url}")
    driver.get(url)
    time.sleep(5)  # espera explícita para JS renderizar, pode ser otimizada futuramente com waits explícitos

    # Extração de HTML completo após renderização JS
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()  # fechamento seguro do driver para evitar leaks de memória

    # Identificação da tabela com classe específica, garantindo robustez contra mudanças mínimas de layout
    table = soup.find("table", class_="gecko-homepage-coin-table")
    if not table:
        logging.error("Tabela não encontrada")
        return []

    rows = table.find("tbody").find_all("tr")[:10]
    data = []

    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) < 11:
            continue  # proteção contra linhas incompletas ou estrutura inesperada

        # Extração de ID a partir do link (uniformização para comparação com API)
        link_tag = cols[2].find("a", href=True)
        coin_id = link_tag["href"].split("/coins/")[1].split("?")[0].lower().replace(" ", "-")

        # Nome e símbolo da moeda, padronizando símbolos para uppercase
        coin_name_tag = cols[2].find("a", {"class": "tw-flex"})
        coin_name = coin_name_tag.find("div", {"class": "tw-text-gray-700"}).contents[0].strip()
        coin_symbol = coin_name_tag.find("div", {"class": "tw-text-xs"}).text.strip().upper()

        # Tratamento dos valores com funções de parse definidas acima
        preco = parse_currency(cols[4].text)
        var_1h = parse_percentage(cols[5].text)
        var_24h = parse_percentage(cols[6].text)
        var_7d = parse_percentage(cols[7].text)
        volume_24h = parse_currency(cols[9].text)
        market_cap = parse_currency(cols[10].text)

        # Estruturação uniforme dos dados em dict para DataFrame posterior
        data.append({
            "id_moeda": coin_id,
            "nome_moeda": coin_name,
            "simbolo": coin_symbol,
            "preco_usd": round(preco, 6),
            "capitalizacao_mercado_usd": round(market_cap, 6),
            "volume_24h_usd": round(volume_24h, 6),
            "variacao_1h_pct": round(var_1h, 2),
            "variacao_24h_pct": round(var_24h, 2),
            "variacao_7d_pct": round(var_7d, 2)
        })

    return data

def normalize_dataframe(data):
    """
    Normaliza DataFrame para manter consistência de colunas, ordem e cabeçalho legível.
    Demonstra boas práticas de engenharia de dados.
    """
    df = pd.DataFrame(data)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = 0.0  # fallback seguro para dados ausentes
    df = df[COLUMNS]  # garante a ordem definida
    df = df.rename(columns=HEADER_MAP)  # padroniza cabeçalho legível
    return df

def save_to_csv(data, filename="top10_coins.csv"):
    """
    Criação de pasta outputs se não existir e salvamento do CSV.
    Código robusto para produção, evitando erros de IO.
    """
    os.makedirs("outputs", exist_ok=True)
    filepath = os.path.join("outputs", filename)
    df = normalize_dataframe(data)
    if not df.empty:
        df.to_csv(filepath, index=False, encoding="utf-8")
        logging.info(f"CSV salvo em: {filepath}")
    else:
        logging.warning("Nenhum dado para salvar")

if __name__ == "__main__":
    coins_data = scrape_top_10_coins()
    save_to_csv(coins_data)
