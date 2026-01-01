from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

url = "https://www.sunbeaminfo.in/internship"
driver.get(url)
driver.implicitly_wait(5)

print("Page Title\n", driver.title)

internship_info = []

para = driver.find_elements(By.CSS_SELECTOR, ".main_info.wow.fadeInUp")
for p in para:
    if p.text.strip():
        internship_info.append(p.text.strip())

table_rows = driver.find_elements(By.TAG_NAME, "tr")

batches = []

for row in table_rows:
    cols = row.find_elements(By.TAG_NAME, "td")

    if len(cols) < 8:
        continue

    batch_data = {
        "sr": cols[0].text,
        "batch": cols[1].text,
        "batch_duration": cols[2].text,
        "start_date": cols[3].text,
        "end_date": cols[4].text,
        "time": cols[5].text,
        "fees": cols[6].text,
        "download": cols[7].text
    }

    batches.append(batch_data)

final_data = {
    "page_title": driver.title,
    "url": url,
    "internship_information": internship_info,
    "internship_batches": batches
}

with open("sunbeam_internship.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=4, ensure_ascii=False)

print("✅ JSON file created: sunbeam_internship.json")

driver.quit()
