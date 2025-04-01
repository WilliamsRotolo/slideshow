
import requests
from bs4 import BeautifulSoup
import json
import subprocess

# === PARTE 1: Estrazione annunci dal sito ===

url = "https://www.rotoloauto.com/lista-veicoli/"
print("🚀 Avvio scraping da:", url)

try:
    print("🔗 Invio richiesta HTTP...")
    response = requests.get(url)
    response.raise_for_status()
    print("✅ Pagina caricata correttamente.")
except Exception as e:
    print(f"❌ Errore nella richiesta: {e}")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')
print("🔎 Cerco tutti i div con class 'ga-vehicles-list-item'...")
annunci = soup.find_all('div', class_='ga-vehicles-list-item')
print(f"📦 Trovati {len(annunci)} annunci.")

if not annunci:
    with open("debug_rotolo.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("⚠️ Nessun annuncio trovato. HTML salvato in 'debug_rotolo.html'")
    exit()

lista_annunci = []

for idx, annuncio in enumerate(annunci, start=1):
    try:
        print(f"\n➡️ Elaboro annuncio {idx}...")

        titolo = annuncio.find("a", class_="ga-title").get_text(strip=True)
        prezzo = annuncio.find("div", class_="ga-price").get_text(strip=True)
        immagine = annuncio.find("img", class_="ga-main-image")["src"]
        link = annuncio.find("a", class_="ga-title")["href"]
        sottotitolo = annuncio.find("div", class_="ga-subtitle").get_text(strip=True)

        try:
            anno, km = map(str.strip, sottotitolo.split("|"))
        except:
            anno, km = "", ""

        link_completo = link if link.startswith("http") else f"https://www.rotoloauto.com{link}"
        immagine_completa = immagine if immagine.startswith("http") else f"https:{immagine}"

        lista_annunci.append({
            "title": titolo,
            "price": prezzo,
            "year": anno,
            "km": km,
            "image_url": immagine_completa,
            "link": link_completo
        })

    except Exception as e:
        print(f"❌ Errore durante l'annuncio {idx}: {e}")

# === PARTE 2: Salvataggio in JSON ===

filename = "stock_rotolo_annunci.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(lista_annunci, f, ensure_ascii=False, indent=2)

print(f"\n✅ Salvati {len(lista_annunci)} annunci in '{filename}' ✅")

# === PARTE 3: Push automatico su GitHub ===

def push_to_github():
    print("📤 Faccio push su GitHub...")
    try:
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", "Aggiornamento automatico JSON"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Push eseguito con successo.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nel push: {e}")

push_to_github()
