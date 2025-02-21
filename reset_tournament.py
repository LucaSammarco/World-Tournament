import json

def reset_tournament():
    """Reinizializza il torneo quando termina."""
    try:
        with open("full_countries.json", "r", encoding="utf-8") as f:
            countries = json.load(f)["countries"]
        
        data = {
            "round": 1,
            "remaining": countries,
            "total_countries": len(countries),
            "processed_countries": []  # Resetta i paesi processati
        }
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Torneo reinizializzato con {len(countries)} paesi.")
    except Exception as e:
        print(f"❌ Errore durante il reset del torneo: {e}")

if __name__ == "__main__":
    reset_tournament()