import tweepy
import logging
import os

# Configura il logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", encoding="utf-8")
logger = logging.getLogger(__name__)

# Credenziali API prese dalle GitHub Secrets
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Emoji per le mosse di Rock-Paper-Scissors
MOVE_EMOJI = {
    "Rock": "✊",
    "Paper": "📜",
    "Scissors": "✂️"
}

def initialize_twitter_client():
    """Inizializza il client Tweepy."""
    try:
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        logger.info("✅ Client API v2 inizializzato con successo.")
        return client
    except Exception as e:
        logger.error(f"❌ Errore durante l'inizializzazione del client API v2: {e}")
        return None

def format_match_tweet(round_num, remaining_count, country1, move1, country2, move2, winner):
    """Genera il testo del tweet per un match con tono aggressivo e 'uses' come verbo."""
    # Creiamo gli hashtag dai nomi dei paesi, rimuovendo spazi e caratteri speciali
    hashtag1 = "#" + country1["name"].replace(" ", "").replace(",", "").replace("-", "")
    hashtag2 = "#" + country2["name"].replace(" ", "").replace(",", "").replace("-", "")
    
    tweet = (f"\U0001F6E1️ Round {round_num} | Countries left: {remaining_count}\n\n"
             f"⚔️ {country1['emoji']} {hashtag1} vs {country2['emoji']} {hashtag2} ⚔️\n\n"
             f"{MOVE_EMOJI[move1]} {hashtag1} uses {move1}\n\n"
             f"{MOVE_EMOJI[move2]} {hashtag2} uses {move2}\n\n")
    
    if winner:
        winner_hashtag = "#" + winner["name"].replace(" ", "").replace(",", "").replace("-", "")
        loser_hashtag = hashtag2 if winner == country1 else hashtag1
        tweet += f"🏆 {winner['emoji']} {winner_hashtag} DEFEATS {loser_hashtag} and ADVANCES!"
    else:  # Pareggio
        tweet += f"🏆 Stalemate! Both advance to fight another day."
    
    return tweet

def post_tweet(text, img_path=None):
    """Pubblica un tweet con il testo fornito e, se presente, un'immagine."""
    client = initialize_twitter_client()
    if client:
        try:
            if img_path:
                auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
                auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                api = tweepy.API(auth)
                media = api.media_upload(img_path)
                client.create_tweet(text=text, media_ids=[media.media_id])
                logger.info("✅ Tweet con immagine pubblicato con successo!")
            else:
                client.create_tweet(text=text)
                logger.info("✅ Tweet pubblicato con successo!")
        except tweepy.TweepyException as e:
            logger.error(f"❌ Errore durante il tweet: {e}")
    else:
        logger.warning("⚠️ Client non inizializzato. Tweet non inviato.")