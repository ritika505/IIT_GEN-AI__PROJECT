import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

BASE_URL = "https://sunbeaminfo.in"
driver.get(BASE_URL)

output = []


about_menu = wait.until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'About Us')]"))
)
ActionChains(driver).move_to_element(about_menu).perform()
time.sleep(1)


driver.find_element(By.XPATH, "//a[contains(text(),'About Sunbeam')]").click()
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
time.sleep(2)


about_text = []

paragraphs = driver.find_elements(By.XPATH, "//div[contains(@class,'container')]//p")
for p in paragraphs:
    text = p.text.strip()
    if text and len(text) > 40:
        about_text.append(text)

output.append("===== ABOUT SUNBEAM =====")
output.extend(about_text)
output.append("")

# GO TO BRANCHES 
about_menu = wait.until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'About Us')]"))
)
ActionChains(driver).move_to_element(about_menu).perform()
time.sleep(1)

driver.find_element(By.XPATH, "//a[contains(text(),'Branches')]").click()
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
time.sleep(2)

output.append("===== BRANCHES =====")

# GET ALL BRANCH CARDS 
branch_cards = driver.find_elements(
    By.XPATH,
    "//a[contains(text(),'View More')]/ancestor::div[contains(@class,'col')]"
)

branch_links = []
for card in branch_cards:
    try:
        link = card.find_element(By.XPATH, ".//a[contains(text(),'View More')]")
        name = card.text.split("\n")[0].strip()
        branch_links.append((name, link.get_attribute("href")))
    except:
        pass

#SCRAPE EACH BRANCH 
for branch_name, branch_url in branch_links:
    driver.get(branch_url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)

    output.append(f"--- {branch_name.upper()} ---")

    sections = driver.find_elements(By.XPATH, "//p | //li")
    seen = set()

    for sec in sections:
        text = sec.text.strip()
        if text and len(text) > 20 and text not in seen:
            seen.add(text)
            output.append(text)

    #  EXTRA HINJAWADI DETAILS 
    if "Hinjawadi" in branch_name:
        output.append("### HINJAWADI ADDITIONAL DETAILS ###")

        # Detailed paragraphs
        try:
            hinj_paragraphs = driver.find_elements(
                By.XPATH, "//div[contains(@class,'container')]//p"
            )
            for p in hinj_paragraphs:
                text = p.text.strip()
                if text and len(text) > 20:
                    output.append("Hinjawadi Detail: " + text)
        except:
            pass

        # Contact information
        try:
            contacts = driver.find_elements(
                By.XPATH, "//div[contains(@class,'container')]//li"
            )
            for c in contacts:
                text = c.text.strip()
                if text and "Pune" in text:
                    output.append("Contact: " + text)
        except:
            pass

    output.append("")

driver.quit()


with open("sunbeam_about_us.txt", "w", encoding="utf-8") as f:
    for line in output:
        f.write(line + "\n")

print("✅ About Us & Branches data (with Hinjawadi details) saved to sunbeam_about_us.txt")
