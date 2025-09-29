import os
import requests
import pandas as pd
import pytz
import logging
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
from src.tools import Tools

tools = Tools()
load_dotenv()

def get_env_var(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise EnvironmentError(f"Variável obrigatória '{name}' não encontrada no .env")
    return v

# Variáveis do .env
API_URL_EXCHANGES = "https://api.coingecko.com/api/v3/exchanges"
TIMEZONE = get_env_var("TIMEZONE")
RATE_LIMIT_DELAY = int(get_env_var("RATE_LIMIT_DELAY"))

TIMEZONE_BR = pytz.timezone(TIMEZONE)

# Colunas de exchanges, mapemaneto para tratamento pós extração dos dados;;;
COLUMNS_EXCHANGES = ["id_exchange", "nome_exchange", "trust_score", "volume_24h_btc", "ultima_atualizacao"]
HEADER_MAP_EXCHANGES = {
    "id_exchange": "ID Exchange",
    "nome_exchange": "Exchange",
    "trust_score": "Trust Score",
    "volume_24h_btc": "Volume 24h (BTC)",
    "ultima_atualizacao": "Última Atualização"
}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

#tratametno padrao de valores monetários. 
def safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

# ========== EXCHANGES ==========
#Fetch dos dados de cambio. 
def fetch_exchanges_data(per_page: int = 20) -> List[Dict[str, Any]]:
    try:
        logging.info("Iniciando coleta das top %d exchanges...", per_page)
        response = requests.get(API_URL_EXCHANGES, params={"per_page": per_page, "page": 1}, timeout=15)
        response.raise_for_status()
        data = response.json()

        exchanges_data = []
        for ex in data:
            exchanges_data.append({
                "id_exchange": ex.get("id"),
                "nome_exchange": ex.get("name"),
                "trust_score": ex.get("trust_score"),
                "volume_24h_btc": safe_float(ex.get("trade_volume_24h_btc")),
                "ultima_atualizacao": datetime.now(TIMEZONE_BR).strftime("%Y-%m-%d %H:%M:%S")
            })

        time.sleep(RATE_LIMIT_DELAY)
        return exchanges_data

    except requests.exceptions.RequestException as e:
        logging.error("Erro ao buscar dados da API de exchanges: %s", e)
        return []

# ========== NORMALIZAÇÃO ==========
def normalize_exchanges(data: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    for col in COLUMNS_EXCHANGES:
        if col not in df.columns:
            df[col] = None
    df = df.rename(columns=HEADER_MAP_EXCHANGES)
    return df[list(HEADER_MAP_EXCHANGES.values())]

# ========== MAIN ==========
def main():
    exchanges_data = fetch_exchanges_data()

    if exchanges_data:
        df = normalize_exchanges(exchanges_data)
        tools.save_to_csv(df, filename="exchanges_output.csv")
    else:
        logging.warning("Nenhum dado coletado. CSV não gerado.")

if __name__ == "__main__":
    main()
