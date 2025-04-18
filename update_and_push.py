import requests
from bs4 import BeautifulSoup
import json
import time
import random

base_url = "https://www.rotoloauto.com/lista-veicoli/"
output_file = "stock_rotolo_annunci.json"
offset = 0
step = 20
pagina = 1
lista_annunci = []

print("🚗 Inizio scraping multi-pagina da RotoloAuto...\n")

while True:
    url = base_url if offset == 0 else f"{base_url}?offset={offset}"
    print(f"📄 Pagina {pagina} - URL: {url}")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    annunci_html = soup.find_all('div', class_='ga-vehicles-list-item')

    if not annunci_html:
        print("🛑 Nessun annuncio trovato, fine delle pagine.")
        break

    print(f"   ➕ Trovati {len(annunci_html)} annunci")

    for annuncio in annunci_html:
        try:
            titolo_tag = annuncio.find("a", class_="ga-title")
            titolo = titolo_tag.get_text(strip=True) if titolo_tag else ""

            prezzo_tag = annuncio.find("div", class_="ga-price")
            prezzo = prezzo_tag.get_text(strip=True) if prezzo_tag else ""

            link = titolo_tag["href"] if titolo_tag and titolo_tag.has_attr("href") else ""
            link_completo = link if link.startswith("http") else f"https://www.rotoloauto.com{link}"

            img_tag = annuncio.find("img", class_="ga-main-image")
            immagine = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
            immagine_completa = immagine if immagine.startswith("http") else f"https:{immagine}"

            anno, km = "", ""
            info_list = annuncio.find("ul", class_="ga-info")
            if info_list:
                items = info_list.find_all("li")
                if len(items) >= 6:
                    prima_riga = items[0].get_text(strip=True)
                    if "," in prima_riga:
                        data = prima_riga.split(",")[1].strip()
                        if "/" in data:
                            mese, anno_parsato = data.split("/")
                            anno = anno_parsato.strip()
                    km = items[5].get_text(strip=True)

            lista_annunci.append({
                "titolo": titolo,
                "prezzo": prezzo,
                "anno": anno,
                "km": km,
                "link": link_completo,
                "immagine": immagine_completa
            })

        except Exception as e:
            print(f"   ⚠️ Errore su un annuncio: {e}")
            continue

    offset += step
    pagina += 1
    time.sleep(1)  # Rispetto per il server

# === DEDUPLICAZIONE ===
print("\n🧹 Avvio deduplicazione...")

visti = set()
deduplicati = []

for annuncio in lista_annunci:
    chiave = (
        annuncio.get("titolo", "").strip().lower(),
        annuncio.get("prezzo", "").strip().lower(),
        annuncio.get("anno", "").strip().lower(),
        annuncio.get("km", "").strip().lower()
    )
    if chiave not in visti:
        visti.add(chiave)
        deduplicati.append(annuncio)

print(f"✅ Da {len(lista_annunci)} annunci totali → {len(deduplicati)} unici")

# === MESCOLAMENTO ===
random.shuffle(deduplicati)
print("🔀 Annunci mescolati in ordine casuale.")

# === SALVATAGGIO ===
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(deduplicati, f, ensure_ascii=False, indent=2)

print(f"\n💾 File salvato come: {output_file}")
