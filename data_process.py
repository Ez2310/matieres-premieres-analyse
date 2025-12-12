import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

# Configuration simulée
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')

# Prix de base réalistes par catégorie
PRIX_BASE_CATEGORIE = {
    "énergie": {"min": 50, "max": 120, "vol": 0.03},
    "métal": {"min": 1500, "max": 2500, "vol": 0.02},
    "agricole": {"min": 300, "max": 800, "vol": 0.04},
    "textile": {"min": 150, "max": 300, "vol": 0.05},
    "chimie": {"min": 800, "max": 1500, "vol": 0.03},
    "industriel": {"min": 40, "max": 120, "vol": 0.04},
    "gaz industriel": {"min": 1000, "max": 2000, "vol": 0.03}
}

# Données persistantes en mémoire (simule une base de données)
_data_store = {}

def get_prix_base(symbole, nom, categorie):
    """Génère un prix de base stable pour une matière"""
    import hashlib
    # Crée une seed unique basée sur le symbole
    seed = int(hashlib.md5(symbole.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    if categorie in PRIX_BASE_CATEGORIE:
        base = PRIX_BASE_CATEGORIE[categorie]
        prix = random.uniform(base["min"], base["max"])
    else:
        prix = random.uniform(100, 500)
    
    # Stocke pour cohérence
    if symbole not in _data_store:
        _data_store[symbole] = {"prix_base": prix, "dernier_prix": prix}
    
    return _data_store[symbole]["prix_base"]

def generer_prix_actuel(symbole, nom, categorie):
    """Génère un prix actuel réaliste avec tendance"""
    if symbole not in _data_store:
        prix_base = get_prix_base(symbole, nom, categorie)
        _data_store[symbole] = {
            "prix_base": prix_base,
            "dernier_prix": prix_base,
            "tendance": random.uniform(-0.01, 0.01)
        }
    
    store = _data_store[symbole]
    volatilite = PRIX_BASE_CATEGORIE.get(categorie, {"vol": 0.03})["vol"]
    
    # Génère un nouveau prix avec tendance + bruit
    variation = store["tendance"] + random.uniform(-volatilite, volatilite)
    nouveau_prix = store["dernier_prix"] * (1 + variation)
    
    # Met à jour
    store["dernier_prix"] = nouveau_prix
    # Légère évolution de la tendance
    store["tendance"] += random.uniform(-0.001, 0.001)
    store["tendance"] = max(-0.02, min(0.02, store["tendance"]))
    
    return round(nouveau_prix, 2)

def get_prix_matiere(symbole):
    """Retourne les données de prix pour une matière"""
    from app import MATIERES_PREMIERES
    
    matiere = next((m for m in MATIERES_PREMIERES if m['symbole'] == symbole), None)
    if not matiere:
        return {"error": f"Matière {symbole} non trouvée"}
    
    nom = matiere['nom']
    categorie = matiere['categorie']
    
    prix_actuel = generer_prix_actuel(symbole, nom, categorie)
    prix_base = _data_store[symbole]["prix_base"]
    
    # Calcule les variations de manière cohérente
    variation_base = (prix_actuel - prix_base) / prix_base * 100
    
    return {
        "prix_actuel": prix_actuel,
        "variation_jour": round(variation_base * random.uniform(0.8, 1.2), 2),
        "variation_semaine": round(variation_base * random.uniform(0.6, 1.4), 2),
        "variation_mois": round(variation_base * random.uniform(0.4, 1.6), 2),
        "variation_annee": round(variation_base * random.uniform(0.2, 2.0), 2),
        "derniere_maj": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_historique(symbole, periode):
    """Retourne l'historique des prix simulé"""
    from app import MATIERES_PREMIERES
    
    matiere = next((m for m in MATIERES_PREMIERES if m['symbole'] == symbole), None)
    if not matiere:
        return {'labels': [], 'prix': []}
    
    # Initialise si nécessaire
    if symbole not in _data_store:
        get_prix_matiere(symbole)
    
    store = _data_store[symbole]
    prix_courant = store["dernier_prix"]
    volatilite = PRIX_BASE_CATEGORIE.get(matiere['categorie'], {"vol": 0.03})["vol"]
    
    now = datetime.now()
    
    if periode == '1d':  # 24 points sur 24h
        labels = [(now - timedelta(hours=23-i)).strftime('%H:%M') for i in range(24)]
        prix = []
        prix_temp = prix_courant
        for i in range(24):
            variation = random.uniform(-volatilite/2, volatilite/2)
            prix_temp = prix_temp * (1 + variation)
            prix.append(round(prix_temp, 2))
    
    elif periode == '7d':  # 7 jours
        labels = [(now - timedelta(days=6-i)).strftime('%d/%m') for i in range(7)]
        prix = []
        prix_temp = prix_courant
        for i in range(7):
            variation = random.uniform(-volatilite, volatilite)
            prix_temp = prix_temp * (1 + variation)
            prix.append(round(prix_temp, 2))
    
    else:  # 'mois' - 30 jours
        labels = [(now - timedelta(days=29-i)).strftime('%d/%m') for i in range(30)]
        prix = []
        prix_temp = prix_courant
        for i in range(30):
            variation = random.uniform(-volatilite*1.5, volatilite*1.5)
            prix_temp = prix_temp * (1 + variation)
            prix.append(round(prix_temp, 2))
    
    return {'labels': labels, 'prix': prix}

def get_indicateurs(symbole, periode='1mo'):
    """Retourne les indicateurs techniques simulés"""
    from app import MATIERES_PREMIERES
    
    matiere = next((m for m in MATIERES_PREMIERES if m['symbole'] == symbole), None)
    if not matiere:
        return {'error': 'Matière non trouvée'}
    
    # Génère un historique pour calculer les indicateurs
    hist_data = get_historique(symbole, periode)
    if not hist_data['prix']:
        return {'error': 'Pas de données historiques'}
    
    prix = np.array(hist_data['prix'])
    
    # Moyennes mobiles
    ma7 = round(np.mean(prix[-7:]), 2) if len(prix) >= 7 else None
    ma30 = round(np.mean(prix[-30:]), 2) if len(prix) >= 30 else None
    ma90 = round(np.mean(prix[-90:]), 2) if len(prix) >= 90 else None
    
    # Médiane
    mediane30 = round(np.median(prix[-30:]), 2) if len(prix) >= 30 else None
    
    # Volatilité (écart-type des variations)
    if len(prix) > 1:
        returns = np.diff(prix) / prix[:-1]
        vol7 = round(np.std(returns[-7:]), 4) if len(returns) >= 7 else None
        vol30 = round(np.std(returns[-30:]), 4) if len(returns) >= 30 else None
        vol90 = round(np.std(returns[-90:]), 4) if len(returns) >= 90 else None
    else:
        vol7 = vol30 = vol90 = None
    
    # Score de tendance (basé sur régression linéaire)
    if len(prix) >= 10:
        x = np.arange(len(prix))
        slope, _ = np.polyfit(x, prix, 1)
        volatility = np.std(prix)
        if volatility > 0:
            score = int(np.clip((slope / volatility) * 100 + 50, 0, 100))
        else:
            score = 50
    else:
        score = 50
    
    # Volume simulé
    prix_moyen = np.mean(prix) if len(prix) > 0 else 100
    volume = int(random.uniform(1000, 10000) * (prix_moyen / 100))
    
    return {
        'ma7': ma7,
        'ma30': ma30,
        'ma90': ma90,
        'mediane30': mediane30,
        'vol7': vol7,
        'vol30': vol30,
        'vol90': vol90,
        'score_tendance': score,
        'volume': volume
    }


    
