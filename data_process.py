import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

# Chargement configuration
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')

# Prix de base réalistes par catégorie
PRIX_BASE_CATEGORIE = {
    "énergie": {"min": 50, "max": 120, "vol": 0.03, "choc": 0.15},
    "métal": {"min": 1500, "max": 2500, "vol": 0.02, "choc": 0.10},
    "agricole": {"min": 300, "max": 800, "vol": 0.04, "choc": 0.20},
    "textile": {"min": 150, "max": 300, "vol": 0.05, "choc": 0.25},
    "chimie": {"min": 800, "max": 1500, "vol": 0.03, "choc": 0.15},
    "industriel": {"min": 40, "max": 120, "vol": 0.04, "choc": 0.20},
    "gaz industriel": {"min": 1000, "max": 2000, "vol": 0.03, "choc": 0.15}
}

# Stockage persistant en mémoire
_data_store = {}

def get_prix_base(symbole, nom, categorie):
    """Génère un prix de base stable pour une matière"""
    import hashlib
    seed = int(hashlib.md5(symbole.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    if categorie in PRIX_BASE_CATEGORIE:
        base = PRIX_BASE_CATEGORIE[categorie]
        prix = random.uniform(base["min"], base["max"])
    else:
        prix = random.uniform(100, 500)
    
    if symbole not in _data_store:
        _data_store[symbole] = {
            "prix_base": prix,
            "dernier_prix": prix,
            "tendance": random.uniform(-0.002, 0.002),
            "historique": []
        }
    
    return _data_store[symbole]["prix_base"]

def generer_prix_actuel(symbole, nom, categorie):
    """Génère un prix actuel réaliste avec tendance"""
    if symbole not in _data_store:
        prix_base = get_prix_base(symbole, nom, categorie)
    
    store = _data_store[symbole]
    volatilite = PRIX_BASE_CATEGORIE.get(categorie, {"vol": 0.03})["vol"]
    
    variation = store["tendance"] + random.uniform(-volatilite, volatilite)
    nouveau_prix = store["dernier_prix"] * (1 + variation)
    
    store["dernier_prix"] = nouveau_prix
    store["tendance"] += random.uniform(-0.001, 0.001)
    store["tendance"] = max(-0.02, min(0.02, store["tendance"]))
    
    store["historique"].append({
        "timestamp": datetime.now(),
        "prix": nouveau_prix,
        "variation": variation
    })
    
    if len(store["historique"]) > 100:
        store["historique"] = store["historique"][-100:]
    
    return round(nouveau_prix, 2)

def get_prix_matiere(symbole):
    """Retourne les données de prix pour une matière + prédictions"""
    from app import MATIERES_PREMIERES
    
    matiere = next((m for m in MATIERES_PREMIERES if m['symbole'] == symbole), None)
    if not matiere:
        return {"error": f"Matière {symbole} non trouvée"}
    
    nom = matiere['nom']
    categorie = matiere['categorie']
    
    prix_actuel = generer_prix_actuel(symbole, nom, categorie)
    prix_base = _data_store[symbole]["prix_base"]
    variation_base = (prix_actuel - prix_base) / prix_base * 100
    
    # CALCUL DES PRÉDICTIONS SIMPLES
    tendance = _data_store[symbole]["tendance"]
    profile = PRIX_BASE_CATEGORIE.get(categorie, {"vol": 0.03, "choc": 0.15})
    
    predictions = {
        "horizon_1j": {
            "continuation": round(prix_actuel * (1 + tendance), 2),
            "range": [
                round(prix_actuel * (1 - profile["vol"]), 2),
                round(prix_actuel * (1 + profile["vol"]), 2)
            ]
        },
        "horizon_7j": {
            "continuation": round(prix_actuel * (1 + tendance * 7), 2),
            "choc_positif": round(prix_actuel * (1 + profile["choc"]), 2),
            "choc_negatif": round(prix_actuel * (1 - profile["choc"]), 2)
        },
        "tendance_force": abs(tendance) * 100,
        "tendance_direction": "HAUSSE" if tendance > 0 else "BAISSE",
        "volatilite": profile["vol"] * 100
    }
    
    return {
        "prix_actuel": prix_actuel,
        "variation_jour": round(variation_base * random.uniform(0.8, 1.2), 2),
        "variation_semaine": round(variation_base * random.uniform(0.6, 1.4), 2),
        "variation_mois": round(variation_base * random.uniform(0.4, 1.6), 2),
        "variation_annee": round(variation_base * random.uniform(0.2, 2.0), 2),
        "derniere_maj": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "predictions": predictions,
        "analyse": {
            "categorie": categorie,
            "risque": "ÉLEVÉ" if profile["vol"] > 0.04 else "MODÉRÉ",
            "potentiel": "FORT" if abs(tendance) > 0.001 else "FAIBLE"
        }
    }

def get_historique(symbole, periode):
    """Retourne l'historique des prix simulé"""
    from app import MATIERES_PREMIERES
    
    matiere = next((m for m in MATIERES_PREMIERES if m['symbole'] == symbole), None)
    if not matiere:
        return {'labels': [], 'prix': []}
    
    if symbole not in _data_store:
        get_prix_matiere(symbole)
    
    store = _data_store[symbole]
    prix_courant = store["dernier_prix"]
    volatilite = PRIX_BASE_CATEGORIE.get(matiere['categorie'], {"vol": 0.03})["vol"]
    
    now = datetime.now()
    
    if periode == '1d':
        labels = [(now - timedelta(hours=23-i)).strftime('%H:%M') for i in range(24)]
        prix = []
        prix_temp = prix_courant
        for i in range(24):
            variation = random.uniform(-volatilite/2, volatilite/2)
            prix_temp = prix_temp * (1 + variation)
            prix.append(round(prix_temp, 2))
    
    elif periode == '7d':
        labels = [(now - timedelta(days=6-i)).strftime('%d/%m') for i in range(7)]
        prix = []
        prix_temp = prix_courant
        for i in range(7):
            variation = random.uniform(-volatilite, volatilite)
            prix_temp = prix_temp * (1 + variation)
            prix.append(round(prix_temp, 2))
    
    else:
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
    
    hist_data = get_historique(symbole, periode)
    if not hist_data['prix']:
        return {'error': 'Pas de données historiques'}
    
    prix = np.array(hist_data['prix'])
    
    ma7 = round(np.mean(prix[-7:]), 2) if len(prix) >= 7 else None
    ma30 = round(np.mean(prix[-30:]), 2) if len(prix) >= 30 else None
    ma90 = round(np.mean(prix[-90:]), 2) if len(prix) >= 90 else None
    
    mediane30 = round(np.median(prix[-30:]), 2) if len(prix) >= 30 else None
    
    if len(prix) > 1:
        returns = np.diff(prix) / prix[:-1]
        vol7 = round(np.std(returns[-7:]), 4) if len(returns) >= 7 else None
        vol30 = round(np.std(returns[-30:]), 4) if len(returns) >= 30 else None
        vol90 = round(np.std(returns[-90:]), 4) if len(returns) >= 90 else None
    else:
        vol7 = vol30 = vol90 = None
    
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

def get_predictions_detail(symbole, horizon='7j'):
    """Retourne des prédictions détaillées"""
    from app import MATIERES_PREMIERES
    
    matiere = next((m for m in MATIERES_PREMIERES if m['symbole'] == symbole), None)
    if not matiere:
        return {"error": "Matière non trouvée"}
    
    prix_data = get_prix_matiere(symbole)
    if "error" in prix_data:
        return prix_data
    
    categorie = matiere['categorie']
    profile = PRIX_BASE_CATEGORIE.get(categorie, {"vol": 0.03, "choc": 0.15})
    prix_actuel = prix_data["prix_actuel"]
    tendance = prix_data["predictions"]["tendance_force"] / 100
    
    if horizon == '1j':
        jours = 1
    elif horizon == '30j':
        jours = 30
    else:
        jours = 7
    
    scenarios = [
        {
            "nom": "Continuité",
            "probabilité": 60,
            "prix_final": round(prix_actuel * (1 + tendance * jours), 2),
            "fourchette": [
                round(prix_actuel * (1 + tendance * jours - profile["vol"]), 2),
                round(prix_actuel * (1 + tendance * jours + profile["vol"]), 2)
            ],
            "description": f"Tendance actuelle se poursuit",
            "declencheurs": ["Marché stable", "Pas de choc majeur"]
        },
        {
            "nom": "Choc positif",
            "probabilité": 20,
            "prix_final": round(prix_actuel * (1 + profile["choc"]), 2),
            "fourchette": [
                round(prix_actuel * (0.95 + profile["choc"]), 2),
                round(prix_actuel * (1.10 + profile["choc"]), 2)
            ],
            "description": f"Événement favorable au {categorie}",
            "declencheurs": ["Nouvelles régulations", "Pénurie", "Accord géopolitique"]
        },
        {
            "nom": "Choc négatif",
            "probabilité": 20,
            "prix_final": round(prix_actuel * (1 - profile["choc"]), 2),
            "fourchette": [
                round(prix_actuel * (0.90 - profile["choc"]), 2),
                round(prix_actuel * (1.05 - profile["choc"]), 2)
            ],
            "description": f"Événement défavorable au {categorie}",
            "declencheurs": ["Récession", "Surproduction", "Conflit"]
        }
    ]
    
    # Recommandation
    if tendance > 0.001 and profile["choc"] > 0.15:
        recommandation = {
            "action": "SURVEILLER POUR ACHAT",
            "confiance": "MODÉRÉE",
            "raison": "Tendance positive avec fort potentiel haussier"
        }
    elif tendance < -0.001:
        recommandation = {
            "action": "SURVEILLER POUR VENTE",
            "confiance": "MODÉRÉE",
            "raison": "Tendance baissière établie"
        }
    else:
        recommandation = {
            "action": "NEUTRE - MAINTENIR",
            "confiance": "ÉLEVÉE",
            "raison": "Marché stable sans signaux forts"
        }
    
    return {
        "symbole": symbole,
        "nom": matiere['nom'],
        "categorie": categorie,
        "prix_actuel": prix_actuel,
        "horizon": horizon,
        "tendance_actuelle": {
            "direction": prix_data["predictions"]["tendance_direction"],
            "force": prix_data["predictions"]["tendance_force"],
            "volatilite": prix_data["predictions"]["volatilite"]
        },
        "scenarios": scenarios,
        "recommandation": recommandation,
        "timestamp": datetime.now().isoformat()
    }
