import os
from dotenv import load_dotenv
import requests
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import sys
import random
import numpy as np

# Charge les variables d'environnement (unifié avec app.py)
load_dotenv()

# Configuration API (uniquement depuis .env maintenant)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')

# Prix simulés pour les matières sans données Yahoo Finance
PRIX_SIMULES = {
    "SILK": {"prix": 150, "variation": 0.5},
    "CASHMERE": {"prix": 300, "variation": 0.8},
    "COAL": {"prix": 120, "variation": -0.3},
    "URANIUM": {"prix": 50, "variation": 0.2},
    "NICKEL": {"prix": 8.5, "variation": 1.2}
}

def get_prix_matiere(symbole):
    # Pour les symboles simulés, retourne des données fictives
    if symbole in PRIX_SIMULES:
        return generer_donnees_simulees(symbole)
    try:
        # Utilise yfinance pour obtenir le prix en temps réel
        ticker = yf.Ticker(symbole)
        data = ticker.history(period="2d")
        if data.empty:
            raise ValueError("Aucune donnée trouvée pour ce symbole.")
        prix_actuel = data['Close'].iloc[-1]
        variation_jour = calculer_variation(data.tail(2))
        variation_semaine = calculer_variation(ticker.history(period="7d"))
        variation_mois = calculer_variation(ticker.history(period="1mo"))
        variation_annee = calculer_variation(ticker.history(period="1y"))
        # Correction: data.index is a pandas Index, not a datetime object.
        # Use pd.Timestamp to get the last timestamp and format it.
        derniere_maj = pd.to_datetime(data.index[-1]).strftime("%Y-%m-%d %H:%M:%S")
        return {
            "prix_actuel": round(prix_actuel, 2),
            "variation_jour": variation_jour,
            "variation_semaine": variation_semaine,
            "variation_mois": variation_mois,
            "variation_annee": variation_annee,
            "derniere_maj": derniere_maj
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération du prix: {str(e)}"}

def calculer_variation(data):
    """Calcule la variation en pourcentage"""
    if len(data) < 2:
        return round(random.uniform(-2, 2), 2)
    
    prix_initial = data['Close'].iloc[0]
    prix_final = data['Close'].iloc[-1]
    variation = ((prix_final - prix_initial) / prix_initial) * 100
    
    return round(variation, 2)

def generer_donnees_simulees(symbole):
    """Génère des données simulées pour les matières sans API"""
    base_data = PRIX_SIMULES.get(symbole, {"prix": 100, "variation": 0.5})
    
    return {
        "prix_actuel": round(base_data["prix"] * random.uniform(0.95, 1.05), 2),
        "variation_jour": round(base_data["variation"] * random.uniform(0.8, 1.2), 2),
        "variation_semaine": round(base_data["variation"] * random.uniform(0.7, 1.3), 2),
        "variation_mois": round(base_data["variation"] * random.uniform(0.5, 1.5), 2),
        "variation_annee": round(base_data["variation"] * random.uniform(0.3, 2.0), 2),
        "derniere_maj": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_historique(symbole, periode):
    """Retourne l'historique des prix pour une matière sur la période demandée.
    periode: '1d' (jour), '7d' (semaine), '1mo' (mois)
    """
    import numpy as np
    from datetime import timedelta
    if symbole in PRIX_SIMULES:
        # Génère des données factices
        now = datetime.now()
        if periode == '1d':
            labels = [(now - timedelta(hours=i)).strftime('%H:%M') for i in reversed(range(24))]
            prix = [round(PRIX_SIMULES[symbole]['prix'] * (1 + np.sin(i/6)*0.01 + np.random.uniform(-0.01,0.01)),2) for i in range(24)]
        elif periode == '7d':
            labels = [(now - timedelta(days=i)).strftime('%d/%m') for i in reversed(range(7))]
            prix = [round(PRIX_SIMULES[symbole]['prix'] * (1 + np.sin(i/2)*0.03 + np.random.uniform(-0.02,0.02)),2) for i in range(7)]
        else:
            labels = [(now - timedelta(days=i)).strftime('%d/%m') for i in reversed(range(30))]
            prix = [round(PRIX_SIMULES[symbole]['prix'] * (1 + np.sin(i/5)*0.05 + np.random.uniform(-0.03,0.03)),2) for i in range(30)]
        return {'labels': labels, 'prix': prix}
    # Pour les symboles Yahoo Finance
    ticker = yf.Ticker(symbole)
    if periode == '1d':
        hist = ticker.history(period='1d', interval='1h')
        labels = [pd.to_datetime(ts).strftime('%H:%M') for ts in hist.index]
    elif periode == '7d':
        hist = ticker.history(period='7d', interval='1d')
        labels = [pd.to_datetime(ts).strftime('%a %d/%m') for ts in hist.index]
    else:
        hist = ticker.history(period='1mo', interval='1d')
        labels = [pd.to_datetime(ts).strftime('%d/%m') for ts in hist.index]
    prix = [round(p,2) for p in hist['Close']]
    return {'labels': labels, 'prix': prix}

def get_indicateurs(symbole, periode='1mo'):
    """Retourne les indicateurs simples pour une matière première : MA, médiane, volatilité, volume, score tendance."""
    import numpy as np
    ticker = yf.Ticker(symbole)
    is_simulated = False
    if symbole in PRIX_SIMULES:
        prix = np.array([PRIX_SIMULES[symbole]['prix'] * (1 + np.sin(i/5)*0.05 + np.random.uniform(-0.03,0.03)) for i in range(90)])
        volume = np.array([np.random.randint(100, 1000) for _ in range(90)])
        index = pd.date_range(end=datetime.now(), periods=90)
        hist = pd.DataFrame({'Close': prix, 'Volume': volume}, index=index)
        is_simulated = True
    else:
        if periode == '1d':
            hist = ticker.history(period='1d', interval='1h')
        elif periode == '7d':
            hist = ticker.history(period='7d', interval='1d')
        elif periode == '3mo':
            hist = ticker.history(period='3mo', interval='1d')
        else:
            hist = ticker.history(period='1mo', interval='1d')
    close = hist['Close'] if 'Close' in hist else pd.Series(dtype=float)
    volume = hist['Volume'] if 'Volume' in hist else None
    # Moyennes mobiles, médiane, volatilité, score tendance
    if is_simulated:
        ma7 = np.mean(close[-7:]) if len(close) >= 7 else None
        ma30 = np.mean(close[-30:]) if len(close) >= 30 else None
        ma90 = np.mean(close[-90:]) if len(close) >= 90 else None
        mediane30 = np.median(close[-30:]) if len(close) >= 1 else None
        returns = np.diff(close) / close[:-1] if len(close) > 1 else np.array([])
        vol7 = np.std(returns[-7:]) if len(returns) >= 7 else None
        vol30 = np.std(returns[-30:]) if len(returns) >= 30 else None
        vol90 = np.std(returns[-90:]) if len(returns) >= 90 else None
        if len(close) >= 30:
            x = np.arange(len(close[-30:]))
            y = close[-30:]
            slope = np.polyfit(x, y, 1)[0]
            score = int(np.clip((slope / (np.std(y) + 1e-6)) * 20 + 50, 0, 100))
        else:
            score = None
        last_volume = int(volume[-1]) if volume is not None and len(volume) else None
    else:
        ma7 = close.rolling(window=7).mean().iloc[-1] if len(close) >= 7 else None
        ma30 = close.rolling(window=30).mean().iloc[-1] if len(close) >= 30 else None
        ma90 = close.rolling(window=90).mean().iloc[-1] if len(close) >= 90 else None
        mediane30 = close[-30:].median() if len(close) >= 1 else None
        vol7 = close.pct_change().rolling(window=7).std().iloc[-1] if len(close) >= 7 else None
        vol30 = close.pct_change().rolling(window=30).std().iloc[-1] if len(close) >= 30 else None
        vol90 = close.pct_change().rolling(window=90).std().iloc[-1] if len(close) >= 90 else None
        if len(close) >= 30:
            x = np.arange(len(close[-30:]))
            y = close[-30:]
            slope = np.polyfit(x, y, 1)[0]
            score = int(np.clip((slope / (y.std() + 1e-6)) * 20 + 50, 0, 100))
        else:
            score = None
        last_volume = int(volume.iloc[-1]) if volume is not None and len(volume) else None
    return {
        'ma7': round(ma7,2) if ma7 is not None else None,
        'ma30': round(ma30,2) if ma30 is not None else None,
        'ma90': round(ma90,2) if ma90 is not None else None,
        'mediane30': round(mediane30,2) if mediane30 is not None else None,
        'vol7': round(vol7,4) if vol7 is not None else None,
        'vol30': round(vol30,4) if vol30 is not None else None,
        'vol90': round(vol90,4) if vol90 is not None else None,
        'score_tendance': score,
        'volume': last_volume
    }