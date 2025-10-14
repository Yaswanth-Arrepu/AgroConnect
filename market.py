from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def fetch_market_data(state_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Automatically install and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://enam.gov.in/web/dashboard/trade-data"
    driver.get(url)

    try:
        state_dropdown_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "min_max_state"))
        )
        time.sleep(3)
        state_dropdown = Select(state_dropdown_element)
        available_states = [option.text.strip() for option in state_dropdown.options]

        if state_name not in available_states:
            print(f"Error: State '{state_name}' not found. Available states: {available_states}")
            driver.quit()
            return pd.DataFrame()

        state_dropdown.select_by_visible_text(state_name)
        refresh_button = driver.find_element(By.ID, "refresh")
        refresh_button.click()
        time.sleep(3)

        table = driver.find_element(By.ID, "data_list")
        rows = table.find_elements(By.TAG_NAME, "tr")

        if len(rows) <= 1:
            print(f"⚠️ Warning: No market data found for '{state_name}' on e-NAM.")
            driver.quit()
            return pd.DataFrame()

        data = []

        def extract_data():
            for row in table.find_elements(By.TAG_NAME, "tr")[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 10:
                    data.append([
                        cols[0].text.strip(),
                        cols[1].text.strip(),
                        cols[2].text.strip(),
                        cols[3].text.strip(),
                        cols[4].text.strip(),
                        cols[5].text.strip(),
                        cols[6].text.strip(),
                        cols[7].text.strip(),
                        cols[8].text.strip(),
                        cols[9].text.strip()
                    ])

        extract_data()

        try:
            pagination_dropdown = Select(driver.find_element(By.ID, "min_max_no_of_list"))
            total_pages = len(pagination_dropdown.options)
            for page_num in range(1, total_pages):
                pagination_dropdown.select_by_index(page_num)
                time.sleep(3)
                extract_data()
        except:
            pass

        driver.quit()
        df = pd.DataFrame(data, columns=[
            "State", "APMC", "Commodity", "Min Price", "Modal Price", "Max Price",
            "Arrivals", "Traded", "Unit", "Date"
        ])
        return df

    except Exception as e:
        print(f"🚨 Error: {e}")
        driver.quit()
        return pd.DataFrame()