import json
import random
import logging
import os
import time
from datetime import datetime

# Importa le tue funzioni esterne
from image_generator import generate_match_image
from reset_tournament import reset_tournament
from twitter_manager import format_match_tweet, post_tweet

# Configura il logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def load_data():
    """Carica i dati del torneo da data.json."""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("data.json non trovato o corrotto. Reinizializzo il torneo.")
        reset_tournament()
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)

def save_data(data):
    """Salva i dati del torneo in data.json."""
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def rock_paper_scissors():
    """Genera una mossa casuale per il gioco sasso-carta-forbici."""
    return random.choice(["Rock", "Paper", "Scissors"])

def save_tournament_history(final_country1, final_country2, winner):
    """Salva lo storico del torneo."""
    try:
        with open("tournament_history.json", "r", encoding="utf-8") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    tournament_id = len(history) + 1
    record = {
        "tournament_id": tournament_id,
        "finale": {"country1": final_country1["name"], "country2": final_country2["name"]},
        "winner": winner["name"],
        "date": datetime.now().isoformat()
    }
    history.append(record)
    with open("tournament_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    logger.info(f"📜 Storico salvato: torneo {tournament_id}, vincitore {winner['name']}")

def play_match(country1, country2, round_num, remaining_count):
    """Simula un match tra due paesi."""
    # Usa i percorsi delle bandiere direttamente dal JSON
    flag1 = country1["flag"].replace("\\", "/")  # Converte \ in / per sicurezza
    flag2 = country2["flag"].replace("\\", "/")

    logger.info(f"Match: {country1['name']} vs {country2['name']}")
    logger.info(f"Tentativo di caricare bandiere: {flag1}, {flag2}")

    # Controlla se i file esistono
    if not os.path.exists(flag1):
        logger.error(f"Bandiera non trovata: {flag1}")
        flag1 = "assets/flags/default.png"
    if not os.path.exists(flag2):
        logger.error(f"Bandiera non trovata: {flag2}")
        flag2 = "assets/flags/default.png"

    # Controlla il fallback
    if not os.path.exists(flag1):
        logger.warning(f"Fallback non trovato: {flag1}. Uso None.")
        flag1 = None
    if not os.path.exists(flag2):
        logger.warning(f"Fallback non trovato: {flag2}. Uso None.")
        flag2 = None

    # Simula il match
    move1, move2 = rock_paper_scissors(), rock_paper_scissors()
    img_path = generate_match_image(country1["name"], flag1, move1,
                                   country2["name"], flag2, move2,
                                   round_num)

    if (move1 == "Rock" and move2 == "Scissors") or \
       (move1 == "Paper" and move2 == "Rock") or \
       (move1 == "Scissors" and move2 == "Paper"):
        winner = country1
        logger.info(f"🏅 {country1['name']} vince con {move1} contro {move2}!")
    elif (move2 == "Rock" and move1 == "Scissors") or \
         (move2 == "Paper" and move1 == "Rock") or \
         (move2 == "Scissors" and move1 == "Paper"):
        winner = country2
        logger.info(f"🏅 {country2['name']} vince con {move2} contro {move1}!")
    else:
        winner = None
        logger.info(f"🤝 Pareggio: {country1['name']} ({move1}) vs {country2['name']} ({move2})")

    # Pubblica il tweet
    tweet_text = format_match_tweet(round_num, remaining_count, country1, move1, country2, move2, winner)
    try:
        post_tweet(text=tweet_text, img_path=img_path)
        logger.info("✅ Tweet pubblicato con successo.")
    except Exception as e:
        if "429" in str(e):
            logger.error("❌ Limite API raggiunto (429). Attendo 15 minuti...")
            time.sleep(900)  # Attendi 15 minuti
            post_tweet(text=tweet_text, img_path=img_path)
            logger.info("✅ Tweet pubblicato dopo attesa.")
        else:
            logger.error(f"❌ Errore tweet: {e}")

    return winner, img_path

def run_tournament():
    """Esegue il torneo con selezione casuale dei paesi."""
    data = load_data()
    remaining = data["remaining"]
    processed = data["processed_countries"]
    round_num = data["round"]
    remaining_count = len(remaining)

    logger.info(f"🔢 Round {round_num} - {remaining_count} paesi rimanenti.")

    if remaining_count == 0:
        logger.info("⚠️ Nessun paese rimanente. Torneo completato o non inizializzato.")
        return

    if remaining_count == 1:
        winner = remaining.pop()
        processed.append(winner)
        logger.info(f"👤 {winner['name']} avanza automaticamente come vincitore!")
        data["remaining"] = processed
        data["processed_countries"] = []
        save_data(data)
        if round_num > 1 and "final_country1" in data and "final_country2" in data:
            save_tournament_history(data["final_country1"], data["final_country2"], winner)
        logger.info(f"🏆 Vincitore del torneo: {winner['name']}")
        reset_tournament()
        return

    # Selezione casuale di due paesi
    country1, country2 = random.sample(remaining, 2)
    logger.info(f"⚔️ Match casuale: {country1['name']} vs {country2['name']}")
    remaining.remove(country1)
    remaining.remove(country2)

    # Imposta i finalisti se siamo all'ultimo match del round
    if remaining_count == 2:
        data["final_country1"] = country1
        data["final_country2"] = country2

    # Esegue il match
    winner, img_path = play_match(country1, country2, round_num, remaining_count)

    # Gestione del vincitore
    if winner:
        processed.append(winner)
    else:
        processed.append(country1)
        processed.append(country2)

    data["remaining"] = remaining
    data["processed_countries"] = processed

    if not remaining:
        data["remaining"] = processed
        data["processed_countries"] = []
        data["round"] += 1
        logger.info(f"🔄 Fine round {round_num}. Nuovo round: {data['round']} con {len(data['remaining'])} paesi.")

    save_data(data)
    logger.info(f"✅ Match completato. Rimangono {len(data['remaining'])} paesi.")

if __name__ == "__main__":
    logger.info("🏁 Avvio del torneo...")
    run_tournament()