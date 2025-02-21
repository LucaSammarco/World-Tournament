import requests
from bs4 import BeautifulSoup
import os
import json
import re
import shutil

URL = "https://en.wikipedia.org/wiki/List_of_national_flags_of_sovereign_states"
FLAGS_DIR = "assets/flags"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def create_flags_folder():
    # Pulisci la directory esistente
    if os.path.exists(FLAGS_DIR):
        shutil.rmtree(FLAGS_DIR)
    os.makedirs(FLAGS_DIR)
    print(f"Cartella {FLAGS_DIR} ripulita e creata.")

def download_flag(url, file_path):
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Bandiera scaricata: {file_path}")
    except requests.RequestException as e:
        print(f"Errore download bandiera {file_path}: {e}")
        return False
    return True

def scrape_countries_and_flags():
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"Errore caricamento pagina: Stato {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        print("Nessuna tabella trovata")
        return []
    
    rows = table.find_all("tr")
    print(f"Trovate {len(rows)} righe nella tabella")

    countries = {}
    for row in rows[1:]:  # Salta l'intestazione
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        # Nome del paese dalla prima colonna
        name_tag = cols[0].find("a", title=True)
        if not name_tag or "Flag of" in name_tag.text:
            continue
        country_name = name_tag.text.strip()
        # Rimuovi qualificatori come "(Islamic Republic)" o "Civil flag of"
        clean_name = re.sub(r"\s*\(.*?\)|\s*(Civil|State|National)\s*flag\s*of\s*", "", country_name).strip()

        # Se il paese esiste già, salta
        if clean_name in countries:
            continue

        # Emoji dal flagicon
        flag_span = cols[0].find("span", class_="flagicon")
        emoji = flag_span.text.strip() if flag_span else ""

        # URL dell'immagine della bandiera
        img_tag = cols[0].find("img")
        if not img_tag or "src" not in img_tag.attrs:
            print(f"Immagine non trovata per {clean_name}")
            continue
        img_url = "https:" + img_tag["src"]

        # Normalizza il nome del file
        file_name = re.sub(r"[^\w\s-]", "", clean_name.lower().replace(" ", "-")) + ".png"
        flag_path = os.path.join(FLAGS_DIR, file_name)

        # Scarica la bandiera
        if download_flag(img_url, flag_path):
            countries[clean_name] = {
                "name": clean_name,
                "emoji": emoji,
                "flag": flag_path
            }
            print(f"Aggiunto: {clean_name} con emoji {emoji}")

    return list(countries.values())

def check_missing_countries(countries):
    # Lista di riferimento con 195 paesi sovrani (ISO 3166-1 semplificata)
    with open("full_countries_reference.json", "r", encoding="utf-8") as f:
        reference = json.load(f)["countries"]
    ref_names = {c["name"] for c in reference}
    scraped_names = {c["name"] for c in countries}
    
    missing = ref_names - scraped_names
    if missing:
        print("Paesi mancanti:")
        for m in sorted(missing):
            print(f"- {m}")
    else:
        print("Nessun paese mancante!")

def main():
    create_flags_folder()
    print("Inizio scraping da Wikipedia...")
    countries = scrape_countries_and_flags()
    with open("full_countries.json", "w", encoding="utf-8") as f:
        json.dump({"countries": countries}, f, indent=4, ensure_ascii=False)
    print(f"full_countries.json compilato con {len(countries)} paesi.")
    
    # Verifica paesi mancanti
    check_missing_countries(countries)

if __name__ == "__main__":
    main()