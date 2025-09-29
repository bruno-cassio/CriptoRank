import os
import logging
import pandas as pd
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Tools:
    """
    Classe utilitária para salvar dados em CSV.
    """

    def __init__(self):
        # Nome da pasta de saída definida no .env ou "data"
        self.output_dir = os.getenv("OUTPUT_DIR", "data")

    def save_to_csv(self, data: pd.DataFrame | List[Dict[str, Any]], filename: str) -> None:
        """
        Salva um DataFrame ou lista de dicionários em CSV.
        """
        try:
            # sobe 1 nível (src -> raiz)
            project_root = os.path.dirname(os.path.dirname(__file__))
            output_path = os.path.join(project_root, self.output_dir)
            os.makedirs(output_path, exist_ok=True)

            filepath = os.path.join(output_path, filename)
            df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)

            if not df.empty:
                df.to_csv(filepath, index=False, encoding="utf-8")
                logging.info("Arquivo salvo em %s com %d registros.", filepath, len(df))
            else:
                logging.warning("Nenhum dado para salvar.")
        except Exception as e:
            logging.error("Erro ao salvar CSV: %s", e)
