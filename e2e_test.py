import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

# L'URL de votre Selenium Grid
SELENIUM_HUB_URL = "http://161.97.93.12:4444/wd/hub"
# L'URL de votre application. Nous devrons l'exposer, par exemple via un Ingress ou un NodePort.
# Pour ce test, nous supposerons qu'elle est accessible à une URL connue.
# Dans un vrai scénario, cette URL serait dynamique.
# Pour l'instant, nous allons modifier notre service K8s en NodePort.
APP_URL = "http://167.86.118.59:31000" 

print(f"Connecting to Selenium Grid at {SELENIUM_HUB_URL}")
print(f"Testing application at {APP_URL}")

options = ChromeOptions()
# Les options 'headless' sont souvent nécessaires dans les pipelines CI/CD
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Remote(
        command_executor=SELENIUM_HUB_URL,
        options=options
    )

    driver.get(APP_URL)

    expected_text = "MOMO"
    actual_text = driver.find_element(By.TAG_NAME, "body").text

    print(f"Page body contains: '{actual_text}'")

    assert expected_text in actual_text
    print("Test PASSED!")

except Exception as e:
    print(f"Test FAILED: {e}")
    sys.exit(1)
finally:
    if 'driver' in locals():
        driver.quit()