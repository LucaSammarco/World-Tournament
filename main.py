import json
import random
import logging
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
        # Carica il file esistente o inizializza una lista vuota
        try:
            with open("tournament_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []

        # Trova l'ID del prossimo torneo
        tournament_id = len(history) + 1

        # Crea il record del torneo
        tournament_record = {
            "tournament_id": tournament_id,
            "finale": {"country1": final_country1["name"], "country2": final_country2["name"]},
            "winner": winner["name"],
            "date": datetime.now().isoformat()
        }

        # Aggiungi il record e salva
        history.append(tournament_record)
        with open("tournament_history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        
        logger.info(f"📜 Storico torneo salvato: {tournament_record}")
    except Exception as e:
        logger.error(f"❌ Errore durante il salvataggio dello storico: {e}")

def play_match(country1, country2, round_num, remaining_count):
    """Simula un match tra due paesi e determina il vincitore."""
    move1, move2 = rock_paper_scissors(), rock_paper_scissors()
    img_path = generate_match_image(country1["name"], country1["flag"], move1,
                                    country2["name"], country2["flag"], move2,
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
    """Gestisce il torneo e avanza i round."""
    data = load_data()
    remaining = data["remaining"]
    processed = data["processed_countries"]
    round_num = data["round"]
    logger.info(f"🔢 Round {round_num} inizia con {len(remaining)} paesi in remaining.")
    
    # Variabili per tracciare la finale
    final_country1 = None
    final_country2 = None
    
    # Continuiamo finché remaining non è vuoto
    while remaining:
        remaining_count = len(remaining)
        
        if remaining_count == 1:  # Numero dispari, l'ultimo passa automaticamente
            logger.info(f"👤 {remaining[0]['name']} passa automaticamente.")
            processed.append(remaining.pop())
            break
        
        # Salviamo i paesi della finale quando remaining ha 2 elementi
        if remaining_count == 2:
            final_country1 = remaining[-1]
            final_country2 = remaining[-2]
        
        country1, country2 = remaining.pop(), remaining.pop()
        winner, img_path = play_match(country1, country2, round_num, remaining_count)
        
        if winner:
            processed.append(winner)
        else:  # Pareggio, entrambi avanzano
            processed.append(country1)
            processed.append(country2)
    
    # Fine del round: trasferiamo processed a remaining
    data["remaining"] = processed
    data["processed_countries"] = []
    data["round"] += 1
    logger.info(f"🔄 Fine round {round_num}. Avanzamento al round {data['round']} con {len(data['remaining'])} paesi in remaining.")
    save_data(data)
    
    # Controlliamo se il nuovo remaining ha 1 solo paese (fine torneo)
    if len(data["remaining"]) == 1:
        winner = data["remaining"][0]
        if final_country1 and final_country2:  # Assicuriamoci di avere i finalisti
            save_tournament_history(final_country1, final_country2, winner)
        logger.info(f"🏆 Vincitore del torneo: {winner['name']}")
        reset_tournament()
    elif len(data["remaining"]) > 1:
        logger.info(f"▶️ Continuazione del torneo con {len(data['remaining'])} paesi.")
        run_tournament()  # Ricorsione per continuare il torneo

if __name__ == "__main__":
    logger.info("🏁 Avvio del torneo...")
    run_tournament()