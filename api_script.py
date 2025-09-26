"""
Script para coleta de dados de criptomoedas via API pública (CoinGecko).
Gera um CSV padronizado com informações de preço, market cap e variações.

Notas:
- Eu  centralizo configurações em .env e faço "fail fast"
  para variáveis obrigatórias.
- Tenho opção de formatar valores para leitura humana (FORMAT_OUTPUT_VALUES)
  ou manter valores numéricos para processamento.
"""

import os
import requests
import pandas as pd
import pytz
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# carrego .env no início do módulo, centralizando as variaveis sensiveis
# permitindo assim também a integração ou consumo com outros projetos, podendo ser alterado se integrado com outras ferramentas
# como django ou tkinter por exemplo. 
load_dotenv()

# helper que garante que variáveis obrigatórias existam (fail-fast)
def get_env_var(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise EnvironmentError(f"Variável obrigatória '{name}' não encontrada no .env")
    return v

# variáveis obrigatórias do ambiente (faço fail-fast para garantir consistência)
API_URL = get_env_var("API_URL")
TIMEZONE = get_env_var("TIMEZONE")
RATE_LIMIT_DELAY = int(get_env_var("RATE_LIMIT_DELAY"))
OUTPUT_FILE = get_env_var("OUTPUT_FILE")
DEFAULT_CURRENCY = get_env_var("DEFAULT_CURRENCY")
DEFAULT_PER_PAGE = int(get_env_var("DEFAULT_PER_PAGE"))

#variáveis opcionais (com default seguro)
FORMAT_OUTPUT_VALUES = os.getenv("FORMAT_OUTPUT_VALUES", "true").lower() in ("1", "true", "yes", "y")

TIMEZONE_BR = pytz.timezone(TIMEZONE)

# Colunas internas (chaves do DataFrame)
COLUMNS = [
    "id_moeda", "nome_moeda", "simbolo",
    "preco_usd", "capitalizacao_mercado_usd", "volume_24h_usd",
    "variacao_1h_pct", "variacao_24h_pct", "variacao_7d_pct",
    "ultima_atualizacao"
]

#mapeamento para cabeçalhos legíveis (nome que vai no CSV)
HEADER_MAP = {
    "id_moeda": "ID Moeda",
    "nome_moeda": "Nome",
    "simbolo": "Símbolo",
    "preco_usd": "Preço (U$)",
    "capitalizacao_mercado_usd": "Capitalização (U$)",
    "volume_24h_usd": "Volume 24h (U$)",
    "variacao_1h_pct": "Variação 1h (%)",
    "variacao_24h_pct": "Variação 24h (%)",
    "variacao_7d_pct": "Variação 7d (%)",
    "ultima_atualizacao": "Última Atualização"
}

# aplicação do Logging para debug geral. 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


def safe_float(value: Any) -> float | None:
    """
   tento converter para float de forma segura. Retorno None se inválido.
    """
    try:
        if value is None:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def fetch_crypto_data(vs_currency: str = DEFAULT_CURRENCY, per_page: int = DEFAULT_PER_PAGE, session: requests.Session = None) -> List[Dict[str, Any]]:
    """
    Busca dados de criptomoedas na API CoinGecko, encaminhando o payload conforme padrao da API aberta.
    """
    session = session or requests.Session()
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d"
    }

    try:
        logging.info("Iniciando coleta das top %d moedas em %s...", per_page, vs_currency)
        response = session.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        #validação extra (evito processar payloads inesperados)
        if not isinstance(data, list) or not data:
            logging.warning("API retornou resposta vazia ou inesperada.")
            return []

        crypto_data = []
        #considerando ser conhecida a predefinição das colunas a serem trabalhadas
        #aqui eu opto por um loop e nao um mapeamento, sendo escalado para niveis maiores
        #(sobre quantidade de dados), um mapeamento seria menos otimizado.
        for coin in data:
            crypto_data.append({
                "id_moeda": coin.get("id"),
                "nome_moeda": coin.get("name"),
                "simbolo": coin.get("symbol"),
                "preco_usd": safe_float(coin.get("current_price")),
                "capitalizacao_mercado_usd": safe_float(coin.get("market_cap")),
                "volume_24h_usd": safe_float(coin.get("total_volume")),
                "variacao_1h_pct": safe_float(coin.get("price_change_percentage_1h_in_currency")),
                "variacao_24h_pct": safe_float(coin.get("price_change_percentage_24h_in_currency")),
                "variacao_7d_pct": safe_float(coin.get("price_change_percentage_7d_in_currency")),
                "ultima_atualizacao": datetime.now(TIMEZONE_BR).strftime("%Y-%m-%d %H:%M:%S")
            })
            logging.debug("Moeda processada: %s (%s)", coin.get("name"), coin.get("symbol"))

        time.sleep(RATE_LIMIT_DELAY)
        return crypto_data

    except requests.exceptions.RequestException as e:
        logging.error("Erro ao buscar dados da API: %s", e)
        return []


def normalize_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    construo DataFrame com colunas fixas, formatação opcional e renomeio cabeçalho.
    - Se FORMAT_OUTPUT_VALUES True: devolvo strings formatadas (U$, %).
    - Se False: mantenho números (floats) e apenas arredondo.
    """
    df = pd.DataFrame(data)

    # garante presença das colunas internas
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None

    # lastro  para formatação
    money_cols = ["preco_usd", "capitalizacao_mercado_usd", "volume_24h_usd"]
    pct_cols = ["variacao_1h_pct", "variacao_24h_pct", "variacao_7d_pct"]

    if FORMAT_OUTPUT_VALUES:
        # formatando para leitura humana (strings)
        def fmt_money(v):
            v = safe_float(v)
            return f"U$ {v:,.2f}" if v is not None else ""

        def fmt_pct(v):
            v = safe_float(v)
            return f"{v:.2f}%" if v is not None else ""

        for col in money_cols:
            df[col] = df[col].apply(fmt_money)

        for col in pct_cols:
            df[col] = df[col].apply(fmt_pct)

    else:
        #mantenho numérico (útil para processamento posterior)
        for col in money_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(6)

        for col in pct_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    # renomeio colunas para cabeçalho legível e retorno na ordem desejada
    readable_order = [HEADER_MAP[c] for c in COLUMNS]
    df = df.rename(columns=HEADER_MAP)
    return df[readable_order]


def save_to_csv(data: List[Dict[str, Any]], filename: str = OUTPUT_FILE) -> None:
    """
   garanto que a pasta exista e salvo o CSV.
    """
    try:
        output_path = Path(filename)
        # crio a pasta (recursivamente) caso não exista
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df = normalize_dataframe(data)
        df.to_csv(output_path, index=False, encoding="utf-8")
        logging.info("Arquivo salvo em %s com %d registros.", output_path, len(df))
    except Exception as e:
        logging.error("Erro ao salvar CSV: %s", e)


def main():
    crypto_data = fetch_crypto_data()

    if crypto_data:
        save_to_csv(crypto_data)
    else:
        logging.warning("Nenhum dado coletado. CSV não gerado.")


if __name__ == "__main__":
    main()
