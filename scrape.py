from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time


# -------------------- COURSE LINKS --------------------
course_links = [
    "https://sunbeaminfo.in/modular-courses/apache-spark-mastery-data-engineering-pyspark",
    "https://sunbeaminfo.in/modular-courses/aptitude-course-in-pune",
    "https://sunbeaminfo.in/modular-courses/core-java-classes",
    "https://sunbeaminfo.in/modular-courses/data-structure-algorithms-using-java",
    "https://sunbeaminfo.in/modular-courses/Devops-training-institute",
    "https://sunbeaminfo.in/modular-courses/dreamllm-training-institute-pune",
    "https://sunbeaminfo.in/modular-courses/machine-learning-classes",
    "https://sunbeaminfo.in/modular-courses/mastering-generative-ai",
    "https://sunbeaminfo.in/modular-courses.php?mdid=57",
    "https://sunbeaminfo.in/modular-courses/mern-full-stack-developer-course",
    "https://sunbeaminfo.in/modular-courses/mlops-llmops-training-institute-pune",
    "https://sunbeaminfo.in/modular-courses/python-classes-in-pune"
]


# -------------------- HEADLESS SETUP --------------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
wait = WebDriverWait(driver, 15)

final_data = []


# -------------------- SMALL HELPERS --------------------
def click_if_present(xp):
    try:
        el = driver.find_element(By.XPATH, xp)
        driver.execute_script("arguments[0].click();", el)
        time.sleep(0.4)
        return True
    except:
        return False


def get_course_name():
    """
    Reads 'Course Name : XYZ' line from header card and returns only XYZ.
    Example line (Core Java page): 'Course Name : Core Java'. [web:26]
    """
    try:
        el = driver.find_element(
            By.XPATH,
            "//*[contains(normalize-space(text()),'Course Name')]"
        )
        txt = el.text.strip()
        # split off label if present
        if ":" in txt:
            return txt.split(":", 1)[1].strip()
        return txt
    except:
        # fallback to h1 (will be 'COURSES' on most pages)
        try:
            return driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            return None


def get_batch_schedule():
    try:
        el = driver.find_element(
            By.XPATH,
            "//*[contains(normalize-space(text()),'Batch Schedule')]"
        )
        return el.text.strip()
    except:
        return None


def get_description():
    try:
        card = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'course-detail') or "
            "      contains(@class,'course-details') or "
            "      contains(@class,'courseinfo')][1] | "
            "//div[contains(@class,'panel')][1]"
        )
    except:
        card = None

    candidates = []
    if card:
        for xp in ["./following-sibling::*", "../following-sibling::*"]:
            try:
                candidates += card.find_elements(By.XPATH, xp)
            except:
                pass

    if not candidates:
        try:
            candidates = driver.find_elements(
                By.XPATH, "//div[contains(@class,'container')]//p"
            )
        except:
            candidates = []

    for c in candidates:
        try:
            ps = c.find_elements(By.XPATH, ".//p")
        except:
            ps = []
        for p in ps:
            t = p.text.strip()
            if t and len(t.split()) > 5:
                return t
    return None


def get_panel_text(panel_title):
    title_xpath = (
        "//a[(contains(@data-toggle,'collapse') or contains(@data-bs-toggle,'collapse') "
        "      or contains(@class,'collapsed')) "
        "   and contains(translate(normalize-space(.), "
        "                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
        "                  'abcdefghijklmnopqrstuvwxyz'), "
        f"         '{panel_title.lower()}')]"
    )

    clicked = click_if_present(title_xpath)
    if not clicked:
        click_if_present(
            "//*[self::h3 or self::h4 or self::div]"
            "[contains(translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), "
            f"'{panel_title.lower()}')]"
        )

    items = []

    try:
        heading = driver.find_element(By.XPATH, title_xpath)
        ctrl = heading.get_attribute("aria-controls")
        if ctrl:
            body = driver.find_element(By.ID, ctrl)
            items = body.find_elements(By.XPATH, ".//li | .//p")
    except:
        pass

    if not items:
        try:
            body = driver.find_element(
                By.XPATH,
                f"{title_xpath}/ancestor::*[1]/following-sibling::*[1]"
            )
            items = body.find_elements(By.XPATH, ".//li | .//p")
        except:
            pass

    out, seen = [], set()
    for it in items:
        t = it.text.strip()
        if not t:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


# -------------------- MAIN LOOP --------------------
for link in course_links:
    print(f"\nScraping: {link}")
    driver.get(link)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1.5)

    data = {
        "url": link,
        "Course Name": None,
        "Duration": None,
        "Batch Schedule": None,
        "Schedule": None,
        "Timings": None,
        "Fees": None,
        "Sections": {
            "Syllabus": [],
            "Prerequisites": []
        }
    }

    # -------- Course Name from header card --------
    data["Course Name"] = get_course_name()

    # -------- BASIC DETAILS FROM HEADER CARD --------
    for field in ["Duration", "Batch Schedule", "Schedule", "Timings", "Fees"]:
        try:
            el = driver.find_element(
                By.XPATH,
                f"//*[contains(normalize-space(text()),'{field}')]"
            )
            data[field] = el.text.strip()
        except:
            pass

    # -------- SYLLABUS & PREREQUISITES FROM PANELS --------
    data["Sections"]["Syllabus"] = get_panel_text("syllabus")
    data["Sections"]["Prerequisites"] = get_panel_text("prerequisites")

    print("  ✔ syllabus items:", len(data["Sections"]["Syllabus"]))
    print("  ✔ prereq items:", len(data["Sections"]["Prerequisites"]))

    final_data.append(data)

# save
with open("sunbeam_modular_courses_full.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=4, ensure_ascii=False)

driver.quit()
print("\n✅ Done")
