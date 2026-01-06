"""
Script d'initialisation de la base de données
"""
import pandas as pd
from pathlib import Path


CSV_FILE_PATH = 'C:/Users/Pc-Marie/Documents/MASTER_APE/S3/Advancing_programming/projet_supply_chain/Projet/data/data.csv'

def setup_database(csv_path=CSV_FILE_PATH):
    """
    Initialise et valide la base de données supply chain.
    
    Args:
        csv_path: Chemin vers le fichier CSV
        
    Returns:
        pd.DataFrame: Données chargées et validées
    """
    try:
        # Charger les données
        data = pd.read_csv(csv_path)
        
        # Convertir la colonne date
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
        
        # Valider les colonnes essentielles
        required_cols = ['Product type', 'date', 'current_stock_level', 'daily_sold_units']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise ValueError(f"Colonnes manquantes: {missing_cols}")
        
        print(f"✅ Base de données initialisée avec succès")
        print(f"   - {len(data)} enregistrements")
        print(f"   - {data['Product type'].nunique()} produits")
        print(f"   - Période: {data['date'].min()} à {data['date'].max()}")
        
        return data
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        raise

if __name__ == "__main__":
    # Test du setup
    data = setup_database()
    print(f"\n📊 Aperçu des données:")
    print(data.head())