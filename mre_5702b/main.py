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





    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    
    
    # enable_jspi = True if os.environ.get("ENABLE_JSPI", "True").lower()=="true" else False

    # if enable_jspi: 
    #     logger.info("Enabling JSPI, not needed 137+")
    #     options.add_experimental_option(
    #     "localState",
    #     {"browser.enabled_labs_experiments": ["enable-experimental-webassembly-jspi@1"]}
    #     )
    
    #options.add_argument("--disable-dev-shm-usage")

    if "CHROME_PATH" in os.environ:
        options.binary_location = os.environ["CHROME_PATH"]
    if "CHROMEDRIVER_PATH" in os.environ:
        service=Service(executable_path=os.environ["CHROMEDRIVER_PATH"])
    else:
        service=None
    if "CHROME_USER_DATA_DIR" in os.environ:
        options.add_argument(f"--user-data-dir={os.environ['CHROME_USER_DATA_DIR']}")

    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    try:
        with webdriver.Chrome(options=options, service=service) as driver:
            version = driver.capabilities["browserVersion"]
            logger.info("Chrome version: %s", version)

            driver.get("about:blank")
            
            exists = driver.execute_script("""
                const hasSuspending = !!WebAssembly.Suspending;
                return hasSuspending;

                """)
            logger.info("WebAssembly.Suspending exists (JSPI is available): %s", exists)

            driver.execute_async_script("let cb=arguments[0];(async()=>{if(window.pyodide){cb();return;}let s=document.createElement('script');s.src='https://cdn.jsdelivr.net/pyodide/v0.28.0/debug/pyodide.js';s.onload=async()=>{window.pyodide=await loadPyodide();cb();};document.head.appendChild(s);})();")



            driver.execute_script("""
                await pyodide.runPythonAsync(`async def noop(i, j):
                    if j == 0:
                        print(f"Hi {i=}{j=}")`);                
                const noop = pyodide.globals.get("noop");
                for (let i = 0; i < 10000; i++) {
                    let p2 = [];
                    for (let j = 0; j < 200; j++) {
                    p2.push(noop(i,j));
                    }
                    await Promise.all(p2);
                }
                                  """)


            logger.info("Success: Ran to the end")

            for entry in driver.get_log("browser"):
                logger.info(entry["message"])
    except Exception:
        logger.exception("Failure: Exception during execution")
        sys.exit(1)


if __name__ == "__main__":
    main()
