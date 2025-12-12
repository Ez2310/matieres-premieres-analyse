"""
PREDICTOR V1 - Système de prévision probabiliste
Combine : Tendances historiques + Aléatoire intelligent
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

class MarketPredictor:
    def __init__(self):
        self.data_dir = "historical_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Configuration des marchés
        self.market_profiles = {
            "énergie": {
                "vol_base": 0.03,  # 3% volatilité de base
                "cyclique": True,
                "saisonnalité": ["hiver", "été"],
                "choc_seuil": 0.15  # 15% pour un choc
            },
            "métal": {
                "vol_base": 0.02,
                "cyclique": False,
                "safe_haven": True,  # valeur refuge
                "choc_seuil": 0.10
            },
            "agricole": {
                "vol_base": 0.04,
                "cyclique": True,
                "saisonnalité_forte": True,
                "choc_seuil": 0.20  # très sensible aux chocs
            }
        }
    
    def get_historical_trend(self, symbol, days=30):
        """Analyse la tendance historique récente"""
        # Pour V1 : données simulées intelligentes
        # Plus tard : intégration Alpha Vantage
        
        # Génère une tendance basée sur le hash du symbole
        import hashlib
        seed = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16) % 100
        random.seed(seed)
        
        # Tendance aléatoire mais persistante
        trend_strength = random.uniform(-0.002, 0.002)  # -0.2% à +0.2%/jour
        
        # Volatilité selon catégorie
        category = self._get_category(symbol)
        vol = self.market_profiles.get(category, {"vol_base": 0.03})["vol_base"]
        
        return {
            "tendance_journalière": trend_strength,
            "volatilité": vol,
            "force_tendance": abs(trend_strength) * 100,  # en %
            "direction": "HAUSSE" if trend_strength > 0 else "BAISSE"
        }
    
    def generate_scenarios(self, symbol, horizon="7j", n_scenarios=3):
        """Génère plusieurs scénarios plausibles"""
        
        # 1. Analyse historique
        hist = self.get_historical_trend(symbol)
        
        # 2. Détermine la catégorie
        category = self._get_category(symbol)
        profile = self.market_profiles.get(category, {})
        
        # 3. Prix actuel simulé (pour V1)
        current_price = self._get_current_price(symbol)
        
        # 4. Génère les scénarios
        scenarios = []
        
        # SCÉNARIO 1 : NORMAL (60% proba)
        normal_price = current_price * (1 + hist["tendance_journalière"] * self._horizon_days(horizon))
        normal_vol = random.uniform(0.8, 1.2) * hist["volatilité"]
        
        scenarios.append({
            "nom": "Continuité",
            "probabilité": 60,
            "prix_final": round(normal_price, 2),
            "fourchette": [
                round(normal_price * (1 - normal_vol), 2),
                round(normal_price * (1 + normal_vol), 2)
            ],
            "description": f"Tendance {hist['direction'].lower()} continue",
            "declencheurs": ["Pas de choc majeur", "Marché stable"]
        })
        
        # SCÉNARIO 2 : CHOC POSITIF (20% proba)
        if profile.get("choc_seuil"):
            choc_pos = current_price * (1 + profile["choc_seuil"])
            scenarios.append({
                "nom": "Choc positif",
                "probabilité": 20,
                "prix_final": round(choc_pos, 2),
                "fourchette": [
                    round(choc_pos * 0.95, 2),
                    round(choc_pos * 1.10, 2)
                ],
                "description": f"Événement favorable au {category}",
                "declencheurs": ["Nouvelles régulations", "Pénurie", "Accord géopolitique"]
            })
        
        # SCÉNARIO 3 : CHOC NÉGATIF (20% proba)
        if profile.get("choc_seuil"):
            choc_neg = current_price * (1 - profile["choc_seuil"])
            scenarios.append({
                "nom": "Choc négatif",
                "probabilité": 20,
                "prix_final": round(choc_neg, 2),
                "fourchette": [
                    round(choc_neg * 0.90, 2),
                    round(choc_neg * 1.05, 2)
                ],
                "description": f"Événement défavorable au {category}",
                "declencheurs": ["Récession", "Surproduction", "Guerre commerciale"]
            })
        
        return {
            "symbole": symbol,
            "catégorie": category,
            "prix_actuel": current_price,
            "horizon": horizon,
            "tendance_actuelle": hist,
            "scénarios": scenarios,
            "recommandation": self._generate_recommendation(scenarios)
        }
    
    def _get_category(self, symbol):
        """Détermine la catégorie d'une matière"""
        from app import MATIERES_PREMIERES
        matiere = next((m for m in MATIERES_PREMIERES if m['symbole'] == symbol), None)
        return matiere['categorie'] if matiere else "énergie"
    
    def _get_current_price(self, symbol):
        """Prix actuel simulé (cohérent avec data_process.py)"""
        # Utilise la même logique que ton système actuel
        import hashlib
        seed = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        categories_ranges = {
            "énergie": (50, 120),
            "métal": (1500, 2500),
            "agricole": (300, 800),
            "textile": (150, 300)
        }
        
        categorie = self._get_category(symbol)
        min_p, max_p = categories_ranges.get(categorie, (100, 500))
        
        return round(random.uniform(min_p, max_p), 2)
    
    def _horizon_days(self, horizon):
        """Convertit l'horizon en jours"""
        if horizon == "1j": return 1
        elif horizon == "7j": return 7
        elif horizon == "30j": return 30
        else: return 7
    
    def _generate_recommendation(self, scenarios):
        """Génère une recommandation basée sur les scénarios"""
        # Logique simple : regarde le scénario le plus probable
        main_scenario = max(scenarios, key=lambda x: x["probabilité"])
        
        if "positif" in main_scenario["nom"].lower():
            return {
                "action": "SURVEILLER POUR ACHAT",
                "confiance": "MODÉRÉE",
                "raison": "Scénario positif dominant"
            }
        elif "négatif" in main_scenario["nom"].lower():
            return {
                "action": "SURVEILLER POUR VENTE",
                "confiance": "MODÉRÉE", 
                "raison": "Risque de choc négatif présent"
            }
        else:
            return {
                "action": "NEUTRE - MAINTENIR",
                "confiance": "ÉLEVÉE",
                "raison": "Continuité probable du marché"
            }

# Interface simple
predictor = MarketPredictor()

def get_prediction(symbol, horizon="7j"):
    """Fonction principale pour l'API"""
    return predictor.generate_scenarios(symbol, horizon)

if __name__ == "__main__":
    # Test
    print("🔮 TEST DU PRÉDICTEUR")
    print("=" * 50)
    
    for symbol in ["BZ=F", "GC=F", "ZW=F", "SILK"]:
        result = get_prediction(symbol, "7j")
        print(f"\n📊 {symbol} - {result['catégorie'].upper()}")
        print(f"Prix actuel: ${result['prix_actuel']}")
        print(f"Tendance: {result['tendance_actuelle']['direction']} ({result['tendance_actuelle']['force_tendance']:.2f}%/j)")
        print(f"Recommandation: {result['recommandation']['action']}")
        
        for scen in result["scénarios"]:
            print(f"  • {scen['nom']} ({scen['probabilité']}%): ${scen['prix_final']}")
