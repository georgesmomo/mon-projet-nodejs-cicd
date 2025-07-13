# Fichier: test_app.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- Configuration ---
# L'URL de ton hub Selenium
SELENIUM_HUB_URL = 'http://161.97.93.12:4444/wd/hub'
# L'URL de l'application à tester (ton VPS sur le port 3000)
APP_URL = 'http://167.86.118.59:3000/'

# --- Initialisation du driver ---
print("Connexion au hub Selenium...")
chrome_options = Options()
# Les options suivantes sont utiles pour tourner dans un environnement comme Jenkins
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# On se connecte à distance au Selenium qui tourne sur ton VPS
driver = webdriver.Remote(
   command_executor=SELENIUM_HUB_URL,
   options=chrome_options
)

try:
    # --- Exécution du test ---
    print(f"Ouverture de l'URL : {APP_URL}")
    driver.get(APP_URL)
    
    # Attendre un peu que la page charge
    time.sleep(2)
    
    # Vérifier le titre de la page
    expected_title = "Express - Hello World"
    actual_title = driver.title
    print(f"Titre attendu: '{expected_title}'")
    print(f"Titre obtenu: '{actual_title}'")
    assert expected_title in actual_title
    print("✅ Test du titre : SUCCÈS")
    
    # Vérifier le contenu d'un élément
    expected_text = "Heyyo"
    element = driver.find_element(By.TAG_NAME, 'h1')
    actual_text = element.text
    print(f"Texte attendu dans H1: '{expected_text}'")
    print(f"Texte obtenu: '{actual_text}'")
    assert expected_text in actual_text
    print("✅ Test du contenu H1 : SUCCÈS")

except AssertionError as e:
    print(f"❌ TEST ÉCHOUÉ: {e}")
    # On force une sortie avec un code d'erreur pour que Jenkins voit l'échec
    exit(1)
finally:
    # --- Nettoyage ---
    print("Fermeture du navigateur.")
    driver.quit()

print("🎉 Tous les tests sont passés avec succès !")