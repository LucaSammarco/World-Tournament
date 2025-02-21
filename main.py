import json
import random
import logging
import os
from datetime import datetime
from image_generator import generate_match_image
from reset_tournament import reset_tournament
from twitter_manager import format_match_tweet, post_tweet

# Configura il logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", encoding="utf-8")
logger = logging.getLogger(__name__)

def load_data():
    """Carica lo stato attuale del torneo da data.json."""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("data.json non trovato o corrotto. Reinizializzazione torneo.")
        reset_tournament()
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)

def save_data(data):
    """Salva lo stato aggiornato del torneo in data.json."""
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def rock_paper_scissors():
    """Simula una mossa di Rock-Paper-Scissors."""
    return random.choice(["Rock", "Paper", "Scissors"])

def save_tournament_history(final_country1, final_country2, winner):
    """Salva i dati della finale e del vincitore in tournament_history.json."""
    try:
        try:
            with open("tournament_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []

        tournament_id = len(history) + 1
        tournament_record = {
            "tournament_id": tournament_id,
            "finale": {"country1": final_country1["name"], "country2": final_country2["name"]},
            "winner": winner["name"],
            "date": datetime.now().isoformat()
        }
        history.append(tournament_record)
        with open("tournament_history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        logger.info(f"📜 Storico torneo salvato: {tournament_record}")
    except Exception as e:
        logger.error(f"❌ Errore durante il salvataggio dello storico: {e}")

def play_match(country1, country2, round_num, remaining_count):
    """Simula un match tra due paesi e determina il vincitore."""
    # Normalizza i percorsi delle bandiere
    flag1 = os.path.normpath(country1["flag"])
    flag2 = os.path.normpath(country2["flag"])
    
    # Debug: stampa i percorsi e verifica esistenza
    logger.info(f"Tentativo di caricare bandiere: {flag1}, {flag2}")
    if not os.path.exists(flag1):
        logger.error(f"Bandiera non trovata: {flag1}")
        flag1 = os.path.normpath("assets/flags/default.png")
    if not os.path.exists(flag2):
        logger.error(f"Bandiera non trovata: {flag2}")
        flag2 = os.path.normpath("assets/flags/default.png")
    
    move1, move2 = rock_paper_scissors(), rock_paper_scissors()
    img_path = generate_match_image(country1["name"], flag1, move1,
                                    country2["name"], flag2, move2,
                                    round_num)
    
    if (move1 == "Rock" and move2 == "Scissors") or (move1 == "Paper" and move2 == "Rock") or (move1 == "Scissors" and move2 == "Paper"):
        winner = country1
        logger.info(f"🏅 {country1['name']} vince!")
    elif (move2 == "Rock" and move1 == "Scissors") or (move2 == "Paper" and move1 == "Rock") or (move2 == "Scissors" and move1 == "Paper"):
        winner = country2
        logger.info(f"🏅 {country2['name']} vince!")
    else:
        winner = None  # Pareggio, entrambi avanzano
        logger.info(f"🤝 Pareggio tra {country1['name']} e {country2['name']}. Entrambi avanzano.")
    
    tweet_text = format_match_tweet(round_num, remaining_count, country1, move1, country2, move2, winner)
    post_tweet(text=tweet_text, img_path=img_path)
    
    return winner, img_path

def run_tournament():
    """Esegue un solo match del torneo e aggiorna lo stato."""
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
        logger.info(f"👤 {winner['name']} passa automaticamente ed è il vincitore!")
        data["remaining"] = processed
        data["processed_countries"] = []
        save_data(data)
        
        if round_num > 1 and "final_country1" in data and "final_country2" in data:
            save_tournament_history(data["final_country1"], data["final_country2"], winner)
        logger.info(f"🏆 Vincitore del torneo: {winner['name']}")
        reset_tournament()
        return

    country1 = remaining.pop()
    country2 = remaining.pop()
    
    if remaining_count == 2:
        data["final_country1"] = country1
        data["final_country2"] = country2

    winner, img_path = play_match(country1, country2, round_num, remaining_count)
    
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
        logger.info(f"🔄 Fine round {round_num}. Avanzamento al round {data['round']} con {len(data['remaining'])} paesi.")
    
    save_data(data)
    logger.info(f"✅ Match completato. {len(data['remaining'])} paesi rimanenti.")

if __name__ == "__main__":
    logger.info("🏁 Avvio del torneo...")
    run_tournament()