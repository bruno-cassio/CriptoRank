import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from src.tools import Tools

tools = Tools()


TIMEZONE_BR = pytz.timezone("America/Sao_Paulo")


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def navigate_and_scrape_exchanges():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://www.coingecko.com"
    logging.info(f"Acessando {url}")
    driver.get(url)
    time.sleep(2)
    driver.maximize_window()
    time.sleep(1)
    try:

        time.sleep(3)

        try:
            #Tratamento com actionchains, tentativa nativa afim de alcaçar a interação com tela atual. 
            exchanges_btn = driver.find_element(By.XPATH, '//div[text()="Exchanges"]')
            ActionChains(driver).move_to_element(exchanges_btn).click().perform()
            logging.info("Botão 'Exchanges' clicado com sucesso")

            time.sleep(2)

            crypto_exchanges_link = driver.find_element(By.XPATH, '//a[contains(., "Crypto Exchanges")]')
            ActionChains(driver).move_to_element(crypto_exchanges_link).click().perform()
            logging.info("Link 'Crypto Exchanges' clicado com sucesso")

        except:
            
            #em caso de erro de carregamento, caindo pro except, tento atraves do link alternativo a busca do dado. 
            url_alt = "https://www.coingecko.com/en/exchanges"
            driver.get(url_alt)
            # pyautogui.hotkey('ctrl','l')
            # time.sleep(0.5)
            # pyautogui.typewrite(url_alt)
            # time.sleep(1)
            # pyautogui.press('enter')
            time.sleep(2)

        # 3) Esperar a tabela renderizar
        time.sleep(5)

        # 4) Parsear HTML com BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Encontrar tabela principal
        table = soup.find("table")
        if not table:
            logging.error("Tabela de Exchanges não encontrada")
            return []

        rows = table.find("tbody").find_all("tr")[:20]
        data = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            exchange_name = cols[1].get_text(strip=True)
            trust_score = cols[2].get_text(strip=True)
            volume_24h = cols[3].get_text(strip=True)

            data.append({
                "Exchange": exchange_name,
                "Trust Score": trust_score,
                "24h Volume": volume_24h,
                "Última Atualização": datetime.now(TIMEZONE_BR).strftime("%Y-%m-%d %H:%M:%S")
            })

        return data

    except Exception as e:
        logging.error(f"Erro durante a navegação: {e}")
        return []
    finally:
        driver.quit()


if __name__ == "__main__":
    exchanges_data = navigate_and_scrape_exchanges()
    if exchanges_data:
        df = pd.DataFrame(exchanges_data)
        tools.save_to_csv(df, filename="scrapy_exchanges.csv")
    else:
        logging.warning("Nenhum dado de exchange coletado")
