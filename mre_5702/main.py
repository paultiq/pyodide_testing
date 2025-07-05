from selenium import webdriver
import logging
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    file = Path("mre_5702/minimal_bug_demo_28_0_mre2.html")

    assert file.exists()


    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    

    try:
        with webdriver.Chrome(options=options) as driver:

            url = file.resolve().as_uri()
            logger.info(f"Opening {url=}")
            driver.get(url)
            WebDriverWait(driver, 120).until(
                EC.text_to_be_present_in_element((By.ID, "output"), "iteration: 10")
            )
            exists = driver.execute_script("""
                const hasSuspending = !!WebAssembly.Suspending;
                if (hasSuspending) delete WebAssembly.Suspending;
                return hasSuspending;
                """)
            print("WebAssembly.Suspending exists (JSPI is available):", exists)

            logger.info("Success: Ran to the end")

            for entry in driver.get_log("browser"):
                print(entry["message"])
    except Exception:
        logger.exception("Failure: Exception during execution")
    

if __name__ == "__main__":
    main()
