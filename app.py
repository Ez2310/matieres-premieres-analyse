import os
from dotenv import load_dotenv

# Chargement des variables d'environnement AVANT tout
load_dotenv()

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import data_process as dp
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# Liste complète des matières premières
MATIERES_PREMIERES = [
    {"id": 1, "nom": "Pétrole brut (Brent)", "unite": "Baril (bbl)", "symbole": "BZ=F", "categorie": "énergie"},
    {"id": 2, "nom": "Gaz naturel", "unite": "MMBtu", "symbole": "NG=F", "categorie": "énergie"},
    {"id": 3, "nom": "Or", "unite": "Once troy", "symbole": "GC=F", "categorie": "métal"},
    {"id": 4, "nom": "Argent", "unite": "Once troy", "symbole": "SI=F", "categorie": "métal"},
    {"id": 5, "nom": "Cuivre", "unite": "Livre", "symbole": "HG=F", "categorie": "métal"},
    {"id": 6, "nom": "Blé", "unite": "Boisseau", "symbole": "ZW=F", "categorie": "agricole"},
    {"id": 7, "nom": "Maïs", "unite": "Boisseau", "symbole": "ZC=F", "categorie": "agricole"},
    {"id": 8, "nom": "Soja", "unite": "Boisseau", "symbole": "ZS=F", "categorie": "agricole"},
    {"id": 9, "nom": "Café", "unite": "Livre", "symbole": "KC=F", "categorie": "agricole"},
    {"id": 10, "nom": "Cacao", "unite": "Tonne", "symbole": "CC=F", "categorie": "agricole"},
    {"id": 11, "nom": "Sucre", "unite": "Livre", "symbole": "SB=F", "categorie": "agricole"},
    {"id": 12, "nom": "Coton", "unite": "Livre", "symbole": "CT=F", "categorie": "agricole"},
    {"id": 13, "nom": "Aluminium", "unite": "Tonne", "symbole": "ALI=F", "categorie": "métal"},
    {"id": 14, "nom": "Nickel", "unite": "Tonne", "symbole": "NICKEL", "categorie": "métal"},
    {"id": 15, "nom": "Platine", "unite": "Once troy", "symbole": "PL=F", "categorie": "métal"},
    {"id": 16, "nom": "Palladium", "unite": "Once troy", "symbole": "PA=F", "categorie": "métal"},
    {"id": 17, "nom": "Soie", "unite": "Kg", "symbole": "SILK", "categorie": "textile"},
    {"id": 18, "nom": "Cachemire", "unite": "Kg", "symbole": "CASHMERE", "categorie": "textile"},
    {"id": 19, "nom": "Charbon", "unite": "Tonne", "symbole": "COAL", "categorie": "énergie"},
    {"id": 20, "nom": "Uranium", "unite": "Livre", "symbole": "URANIUM", "categorie": "énergie"},
    {"id": 21, "nom": "Essence (RBOB)", "unite": "Gallons", "symbole": "RB=F", "categorie": "énergie"},
    {"id": 22, "nom": "Fioul domestique", "unite": "Gallons", "symbole": "HO=F", "categorie": "énergie"},
    {"id": 23, "nom": "Plomb", "unite": "Tonne", "symbole": "LEAD", "categorie": "métal"},
    {"id": 24, "nom": "Zinc", "unite": "Tonne", "symbole": "ZNC=F", "categorie": "métal"},
    {"id": 25, "nom": "Étain", "unite": "Tonne", "symbole": "TIN", "categorie": "métal"},
    {"id": 26, "nom": "Fer", "unite": "Tonne", "symbole": "FE=F", "categorie": "métal"},
    {"id": 27, "nom": "Acier", "unite": "Tonne", "symbole": "STL=F", "categorie": "métal"},
    {"id": 28, "nom": "Riz", "unite": "Cwt", "symbole": "ZR=F", "categorie": "agricole"},
    {"id": 29, "nom": "Avoine", "unite": "Boisseau", "symbole": "ZO=F", "categorie": "agricole"},
    {"id": 30, "nom": "Huile de palme", "unite": "Tonne", "symbole": "PALMOIL", "categorie": "agricole"},
    {"id": 31, "nom": "Caoutchouc", "unite": "Kg", "symbole": "RUBBER", "categorie": "agricole"},
    {"id": 32, "nom": "Bois d'œuvre", "unite": "Pieds-planche", "symbole": "LBS=F", "categorie": "agricole"},
    {"id": 33, "nom": "Jus d'orange", "unite": "Livre", "symbole": "OJ=F", "categorie": "agricole"},
    {"id": 34, "nom": "Porc maigre", "unite": "Livre", "symbole": "HE=F", "categorie": "agricole"},
    {"id": 35, "nom": "Bœuf vivant", "unite": "Livre", "symbole": "LE=F", "categorie": "agricole"},
    {"id": 36, "nom": "Bétail engraissé", "unite": "Livre", "symbole": "GF=F", "categorie": "agricole"},
    {"id": 37, "nom": "Lait", "unite": "Cwt", "symbole": "DA=F", "categorie": "agricole"},
    {"id": 38, "nom": "Wool (laine)", "unite": "Kg", "symbole": "WOOL", "categorie": "textile"},
    {"id": 39, "nom": "Éthanol", "unite": "Gallons", "symbole": "ETHANOL", "categorie": "énergie"},
    {"id": 40, "nom": "Lithium", "unite": "Tonne", "symbole": "LITHIUM", "categorie": "métal"},
    {"id": 41, "nom": "Terres rares", "unite": "Tonne", "symbole": "RARE", "categorie": "métal"},
    {"id": 42, "nom": "Potasse", "unite": "Tonne", "symbole": "POTASH", "categorie": "agricole"},
    {"id": 43, "nom": "Phosphate", "unite": "Tonne", "symbole": "PHOSPHATE", "categorie": "agricole"},
    {"id": 44, "nom": "Tourteau de soja", "unite": "Tonne", "symbole": "SM=F", "categorie": "agricole"},
    {"id": 45, "nom": "Huile de soja", "unite": "Livre", "symbole": "BO=F", "categorie": "agricole"},
    {"id": 46, "nom": "Gazole", "unite": "Litre", "symbole": "DIESEL", "categorie": "énergie"},
    {"id": 47, "nom": "Plastique (polyéthylène)", "unite": "Tonne", "symbole": "PE=F", "categorie": "chimie"},
    {"id": 48, "nom": "Plastique (polypropylène)", "unite": "Tonne", "symbole": "PP=F", "categorie": "chimie"},
    {"id": 49, "nom": "GNL (Gaz naturel liquéfié)", "unite": "Tonne", "symbole": "LNG=F", "categorie": "énergie"},
    {"id": 50, "nom": "Propane", "unite": "Gallon", "symbole": "LPG=F", "categorie": "énergie"},
    {"id": 51, "nom": "Uranium U3O8 (spot)", "unite": "Livre", "symbole": "UX=F", "categorie": "énergie"},
    {"id": 52, "nom": "Bitume", "unite": "Tonne", "symbole": "BITUMEN", "categorie": "énergie"},
    {"id": 53, "nom": "Bois (pâte à papier)", "unite": "Tonne", "symbole": "PULP=F", "categorie": "agricole"},
    {"id": 54, "nom": "Huile de tournesol", "unite": "Tonne", "symbole": "SUNOIL", "categorie": "agricole"},
    {"id": 55, "nom": "Huile de colza", "unite": "Tonne", "symbole": "RAPESEEDOIL", "categorie": "agricole"},
    {"id": 56, "nom": "Pois", "unite": "Tonne", "symbole": "PEAS", "categorie": "agricole"},
    {"id": 57, "nom": "Lentilles", "unite": "Tonne", "symbole": "LENTILS", "categorie": "agricole"},
    {"id": 58, "nom": "Arachide", "unite": "Tonne", "symbole": "PEANUTS", "categorie": "agricole"},
    {"id": 59, "nom": "Tomate industrielle", "unite": "Tonne", "symbole": "TOMATO", "categorie": "agricole"},
    {"id": 60, "nom": "Banane", "unite": "Tonne", "symbole": "BANANA", "categorie": "agricole"},
    {"id": 61, "nom": "Pomme de terre", "unite": "Tonne", "symbole": "POTATO", "categorie": "agricole"},
    {"id": 62, "nom": "Oignon", "unite": "Tonne", "symbole": "ONION", "categorie": "agricole"},
    {"id": 63, "nom": "Sel", "unite": "Tonne", "symbole": "SALT", "categorie": "industriel"},
    {"id": 64, "nom": "Graphite", "unite": "Tonne", "symbole": "GRAPHITE", "categorie": "métal"},
    {"id": 65, "nom": "Cobalt", "unite": "Tonne", "symbole": "COBALT", "categorie": "métal"},
    {"id": 66, "nom": "Manganèse", "unite": "Tonne", "symbole": "MANGANESE", "categorie": "métal"},
    {"id": 67, "nom": "Vanadium", "unite": "Tonne", "symbole": "VANADIUM", "categorie": "métal"},
    {"id": 68, "nom": "Sable de silice", "unite": "Tonne", "symbole": "SILICASAND", "categorie": "industriel"},
    {"id": 69, "nom": "Hélium", "unite": "m3", "symbole": "HELIUM", "categorie": "gaz industriel"},
    {"id": 70, "nom": "Hydrogène", "unite": "kg", "symbole": "HYDROGEN", "categorie": "gaz industriel"}
]

# Mapping des liens d'actualités
NEWS_BASES = {
    'yahoo': 'https://finance.yahoo.com/quote/',
    'investing': 'https://www.investing.com/commodities/',
    'google': 'https://news.google.com/search?q='
}

def get_news_url(matiere):
    symb = matiere.get('symbole', '').replace('=F','').replace(' ','-').lower()
    cat = matiere.get('categorie','').lower()
    nom = matiere.get('nom','').replace(' ','+').replace("'",'')
    
    if matiere['symbole'] and matiere['symbole'].endswith('=F'):
        return f"{NEWS_BASES['yahoo']}{matiere['symbole']}?p={matiere['symbole']}"
    
    if cat in ['énergie','métal','agricole','chimie','industriel']:
        return f"{NEWS_BASES['investing']}{symb}-news"
    
    return f"{NEWS_BASES['google']}{nom}+actualites"

# Ajout des URLs d'actualités
for m in MATIERES_PREMIERES:
    m['news_url'] = get_news_url(m)

# ==================== ROUTES API ====================

@app.route('/api/matieres', methods=['GET'])
def get_matieres():
    """Retourne la liste des matières premières avec filtrage"""
    query = request.args.get('q', '').lower()
    categorie = request.args.get('categorie', '').lower()
    
    filtered_matieres = MATIERES_PREMIERES
    
    if query:
        filtered_matieres = [m for m in filtered_matieres if query in m['nom'].lower()]
    
    if categorie:
        filtered_matieres = [m for m in filtered_matieres if categorie == m['categorie'].lower()]
    
    return jsonify(filtered_matieres)

@app.route('/api/prix/<int:matiere_id>', methods=['GET'])
def get_prix(matiere_id):
    """Retourne les données de prix + prédictions"""
    matiere = next((m for m in MATIERES_PREMIERES if m['id'] == matiere_id), None)
    
    if not matiere:
        return jsonify({"error": "Matière première non trouvée"}), 404
    
    try:
        data = dp.get_prix_matiere(matiere['symbole'])
        return jsonify({
            **data,
            "matiere": {
                "id": matiere['id'],
                "nom": matiere['nom'],
                "unite": matiere['unite'],
                "categorie": matiere['categorie']
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predictions/<int:matiere_id>', methods=['GET'])
def get_predictions(matiere_id):
    """Retourne les prédictions détaillées"""
    matiere = next((m for m in MATIERES_PREMIERES if m['id'] == matiere_id), None)
    
    if not matiere:
        return jsonify({"error": "Matière première non trouvée"}), 404
    
    try:
        horizon = request.args.get('horizon', '7j')
        predictions = dp.get_predictions_detail(matiere['symbole'], horizon)
        return jsonify(predictions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tendances', methods=['GET'])
def get_tendances():
    """Retourne les tendances pour toutes les matières premières"""
    tendances = []
    for matiere in MATIERES_PREMIERES:
        try:
            data = dp.get_prix_matiere(matiere['symbole'])
            tendances.append({
                "id": matiere['id'],
                "nom": matiere['nom'],
                "unite": matiere['unite'],
                "categorie": matiere['categorie'],
                "data": data
            })
        except Exception as e:
            print(f"Erreur pour {matiere['nom']}: {str(e)}")
    
    return jsonify(tendances)

@app.route('/api/historique/<int:matiere_id>', methods=['GET'])
def historique_prix(matiere_id):
    """Retourne l'historique des prix"""
    matiere = next((m for m in MATIERES_PREMIERES if m['id'] == matiere_id), None)
    if not matiere:
        return jsonify({"error": "Matière première non trouvée"}), 404
    
    periode = request.args.get('periode', 'mois')
    symbole = matiere['symbole']
    
    try:
        if periode == 'jour':
            data = dp.get_historique(symbole, '1d')
            granularite = 'Heure'
        elif periode == 'semaine':
            data = dp.get_historique(symbole, '7d')
            granularite = 'Jour'
        else:
            data = dp.get_historique(symbole, '1mo')
            granularite = 'Jour'
        
        return jsonify({
            'labels': data['labels'],
            'prix': data['prix'],
            'granularite': granularite
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/indicateurs/<int:matiere_id>', methods=['GET'])
def indicateurs_matiere(matiere_id):
    """Retourne les indicateurs techniques"""
    matiere = next((m for m in MATIERES_PREMIERES if m['id'] == matiere_id), None)
    if not matiere:
        return jsonify({"error": "Matière première non trouvée"}), 404
    
    periode = request.args.get('periode', '1mo')
    
    try:
        indicateurs = dp.get_indicateurs(matiere['symbole'], periode)
        return jsonify(indicateurs)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/analyse/<int:matiere_id>', methods=['GET'])
def analyse_matiere(matiere_id):
    """Retourne une analyse complète (prix + prédictions + indicateurs)"""
    matiere = next((m for m in MATIERES_PREMIERES if m['id'] == matiere_id), None)
    if not matiere:
        return jsonify({"error": "Matière première non trouvée"}), 404
    
    try:
        # Prix et prédictions
        prix_data = dp.get_prix_matiere(matiere['symbole'])
        
        # Indicateurs
        indicateurs = dp.get_indicateurs(matiere['symbole'])
        
        # Prédictions détaillées
        predictions = dp.get_predictions_detail(matiere['symbole'])
        
        return jsonify({
            "matiere": {
                "id": matiere['id'],
               
