from selenium import webdriver
import logging
import sys
import os

from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    file = Path("mre_5702/minimal_bug_demo_28_0_mre2.html")

    assert file.exists()

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-blink-features=JavaScriptPromiseIntegration")
    
    #options.add_argument("--disable-dev-shm-usage")

    if "CHROME_PATH" in os.environ:
        options.binary_location = os.environ["CHROME_PATH"]
    if "CHROMEDRIVER_PATH" in os.environ:
        service=Service(executable_path=os.environ["CHROMEDRIVER_PATH"])
    else:
        service=None
    if "CHROME_USER_DATA_DIR" in os.environ:
        options.add_argument(f"--user-data-dir={os.environ['CHROME_USER_DATA_DIR']}")

    try:
        with webdriver.Chrome(options=options, service=service) as driver:
            version = driver.capabilities["browserVersion"]
            logger.info("Chrome version: %s", version)
            url = file.resolve().as_uri()
            logger.info(f"Opening {url=}")
            driver.get(url)

            exists = driver.execute_script("""
                const hasSuspending = !!WebAssembly.Suspending;
                return hasSuspending;
                //if (hasSuspending) delete WebAssembly.Suspending;
                //    return hasSuspending;
                """)
            logger.info("WebAssembly.Suspending exists (JSPI is available): %s", exists)

            WebDriverWait(driver, 120).until(
                EC.text_to_be_present_in_element((By.ID, "output"), "iteration: 10")
            )


            logger.info("Success: Ran to the end")

            for entry in driver.get_log("browser"):
                logger.info(entry["message"])
    except Exception:
        logger.exception("Failure: Exception during execution")
        sys.exit(1)


if __name__ == "__main__":
    main()
