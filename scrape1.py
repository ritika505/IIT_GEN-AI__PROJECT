import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.sunbeaminfo.in/pre-cat"

def scrape_to_json(output_file="precat_data.json"):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        result = {}

        # Find all accordion headers
        headers = driver.find_elements(
            By.XPATH,
            "//a[@data-toggle='collapse']"
        )

        for header in headers:
            title = header.text.strip()
            if not title:
                continue

            # Open accordion
            driver.execute_script("arguments[0].click();", header)
            time.sleep(0.5)

            collapse_id = header.get_attribute("href").split("#")[-1]

            content_div = driver.find_element(By.ID, collapse_id)

            # Extract clean content
            items = []

            # list items
            for li in content_div.find_elements(By.XPATH, ".//li"):
                text = li.text.strip()
                if text:
                    items.append(text)

            # paragraphs
            for p in content_div.find_elements(By.XPATH, ".//p"):
                text = p.text.strip()
                if text and text not in items:
                    items.append(text)

            # table rows (for batch schedule)
            tables = content_div.find_elements(By.XPATH, ".//table")
            table_data = []

            for table in tables:
                rows = table.find_elements(By.XPATH, ".//tr")
                for row in rows:
                    cols = [c.text.strip() for c in row.find_elements(By.XPATH, ".//th | .//td")]
                    if cols:
                        table_data.append(cols)

            result[title] = {
                "content": items,
                "table": table_data
            }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print(f"✅ Data saved to {output_file}")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_to_json()
