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


    if "PYODIDE_VERSION" in os.environ:
        pyodide_version = os.environ.get("PYODIDE_VERSION", "v0.28.0")
        file_body = file.read_text()

        assert "PYODIDE_VERSION" in file_body, "PYODIDE_VERSION in environment but not in the HTML body"

        logger.info("Replacing PYODIDE_VERSION in file_body with %s", pyodide_version)
        file_body_updated = file_body.replace("PYODIDE_VERSION", pyodide_version)

        file.write_text(file_body_updated)



    enable_jspi = True if os.environ["ENABLE_JSPI"].lower()=="true" else False


    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    
    if enable_jspi: 
        logger.info("Enabling JSPI, not needed 137+")
        options.add_experimental_option(
        "localState",
        {"browser.enabled_labs_experiments": ["enable-experimental-webassembly-jspi@1"]}
        )
    
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

            if not enable_jspi:
                logger.info("Disabling JSPI, not needed above below 137")
                driver.execute_script("""
                    const hasSuspending = !!WebAssembly.Suspending;

                    if (hasSuspending) delete WebAssembly.Suspending;
                        return hasSuspending;
                    """)

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
