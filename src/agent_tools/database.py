"""
Script d'initialisation de la base de données
"""
import pandas as pd
from pathlib import Path
from datetime import timedelta, datetime


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
        print(f"📂 Chargement de {csv_path}...")
        data = pd.read_csv(csv_path)
        
        # Convertir la colonne date
        print("📅 Conversion des dates...")
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
        
        # Valider les colonnes essentielles
        required_cols = ['Product type', 'date', 'current_stock_level', 'daily_sold_units']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise ValueError(f"Colonnes manquantes: {missing_cols}")
        
        # Ajouter is_stockout si manquant
        if 'is_stockout' not in data.columns:
            print("➕ Ajout de la colonne 'is_stockout'...")
            data['is_stockout'] = (data['current_stock_level'] == 0).astype(int)
        
        # Gérer les valeurs manquantes
        print("🔧 Nettoyage des données...")
        
        # Remplir les NaN dans daily_sold_units avec 0
        if data['daily_sold_units'].isna().any():
            data['daily_sold_units'] = data['daily_sold_units'].fillna(0)
        
        # Remplir les NaN dans daily_production_units avec 0
        if 'daily_production_units' in data.columns:
            data['daily_production_units'] = data['daily_production_units'].fillna(0)
        
        # S'assurer que les valeurs sont positives
        data['current_stock_level'] = data['current_stock_level'].clip(lower=0)
        data['daily_sold_units'] = data['daily_sold_units'].clip(lower=0)
        
        print(f"✅ Base de données initialisée avec succès")
        print(f"   - {len(data):,} enregistrements")
        print(f"   - {data['Product type'].nunique()} produits: {data['Product type'].unique()[:5].tolist()}")
        print(f"   - Période: {data['date'].min()} à {data['date'].max()}")
        print(f"   - Colonnes: {len(data.columns)}")
        
        return data
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        raise

if __name__ == "__main__":
    # Test du setup
    data = setup_database()
    print(f"\n📊 Aperçu des données:")
    print(data.head())

class DatabaseManager:
    """Gestionnaire de base de données pour la supply chain."""
    
    def __init__(self, data):
        """
        Initialise le gestionnaire avec les données.
        
        Args:
            data: DataFrame pandas contenant les données
        """
        self.data = data.copy()
        
        # Assurer que la colonne 'is_stockout' existe
        if 'is_stockout' not in self.data.columns:
            self.data['is_stockout'] = (self.data['current_stock_level'] == 0).astype(int)
        
        # Convertir la date si ce n'est pas déjà fait
        if not pd.api.types.is_datetime64_any_dtype(self.data['date']):
            self.data['date'] = pd.to_datetime(self.data['date'])
        
        # S'assurer que les données sont triées par date
        self.data = self.data.sort_values('date').reset_index(drop=True)
    
    def get_inventory_data(self, product=None, period_days=90):
        """
        Extrait les données historiques de stock et ventes.
        
        Args:
            product: Nom du produit (None pour tous)
            period_days: Nombre de jours à extraire
            
        Returns:
            pd.DataFrame: Données filtrées
        """
        df = self.data.copy()
        
        # Filtrer par produit si spécifié
        if product:
            df = df[df['Product type'] == product]
        
        # Filtrer par période
        if len(df) > 0:
            end_date = df['date'].max()
            start_date = end_date - timedelta(days=period_days)
            df = df[df['date'] >= start_date]
        
        return df.reset_index(drop=True)
    
    def add_production_record(self, product, date, stock_level, sold_units, 
                             production_units=0, temp_celsius=None, 
                             weather_condition=None, promotion_active=0):
        """
        Ajoute un nouvel enregistrement de production.
        
        Args:
            product: Nom du produit
            date: Date de l'enregistrement
            stock_level: Niveau de stock
            sold_units: Unités vendues
            production_units: Unités produites
            temp_celsius: Température
            weather_condition: Conditions météo
            promotion_active: Promotion active (0/1)
        """
        new_record = {
            'Product type': product,
            'date': pd.to_datetime(date),
            'current_stock_level': stock_level,
            'daily_sold_units': sold_units,
            'daily_production_units': production_units,
            'temp_celsius': temp_celsius,
            'weather_condition': weather_condition,
            'promotion_active': promotion_active,
            'is_stockout': 1 if stock_level == 0 else 0
        }
        
        # Ajouter les autres colonnes avec des valeurs par défaut si elles existent
        for col in self.data.columns:
            if col not in new_record:
                # Utiliser la dernière valeur connue pour ce produit ou une valeur par défaut
                product_data = self.data[self.data['Product type'] == product]
                if len(product_data) > 0 and col in product_data.columns:
                    new_record[col] = product_data[col].iloc[-1]
                else:
                    new_record[col] = None
        
        # Créer un DataFrame avec le nouvel enregistrement
        new_df = pd.DataFrame([new_record])
        
        # Ajouter à la base de données
        self.data = pd.concat([self.data, new_df], ignore_index=True)
        self.data = self.data.sort_values('date').reset_index(drop=True)
        
        print(f"✅ Enregistrement ajouté pour {product} le {date}")
    
    def get_product_stats(self, product, period_days=30):
        """
        Calcule les statistiques pour un produit.
        
        Args:
            product: Nom du produit
            period_days: Période d'analyse
            
        Returns:
            dict: Statistiques du produit
        """
        df = self.get_inventory_data(product, period_days)
        
        if len(df) == 0:
            return None
        
        stats = {
            'total_sales': df['daily_sold_units'].sum(),
            'avg_daily_sales': df['daily_sold_units'].mean(),
            'current_stock': df['current_stock_level'].iloc[-1],
            'min_stock': df['current_stock_level'].min(),
            'max_stock': df['current_stock_level'].max(),
            'stockout_days': (df['is_stockout'] == 1).sum() if 'is_stockout' in df.columns else 0
        }
        
        # Ajouter des stats supplémentaires si disponibles
        if 'Revenue generated' in df.columns:
            stats['total_revenue'] = df['Revenue generated'].sum()
        
        if 'Price' in df.columns:
            stats['avg_price'] = df['Price'].mean()
        
        if 'daily_production_units' in df.columns:
            stats['total_production'] = df['daily_production_units'].sum()
        
        return stats
    
    def get_all_products(self):
        """
        Retourne la liste de tous les produits.
        
        Returns:
            list: Liste des noms de produits
        """
        return self.data['Product type'].unique().tolist()
    
    def get_date_range(self):
        """
        Retourne la période couverte par les données.
        
        Returns:
            dict: Informations sur la période
        """
        return {
            'start': self.data['date'].min(),
            'end': self.data['date'].max(),
            'days': (self.data['date'].max() - self.data['date'].min()).days
        }
    
    def get_product_info(self, product):
        """
        Obtient les informations détaillées d'un produit.
        
        Args:
            product: Nom du produit
            
        Returns:
            dict: Informations du produit
        """
        df = self.data[self.data['Product type'] == product]
        
        if len(df) == 0:
            return None
        
        # Prendre la dernière ligne pour les infos statiques
        latest = df.iloc[-1]
        
        info = {
            'product_type': product,
            'total_records': len(df)
        }
        
        # Ajouter les colonnes statiques si disponibles
        static_cols = ['SKU', 'Price', 'Supplier name', 'Location', 
                      'Lead time', 'Shipping carriers']
        
        for col in static_cols:
            if col in df.columns:
                info[col.lower().replace(' ', '_')] = latest[col]
        
        return info
    
    def get_stockout_history(self, product=None, period_days=90):
        """
        Récupère l'historique des ruptures de stock.
        
        Args:
            product: Nom du produit (None pour tous)
            period_days: Période d'analyse
            
        Returns:
            pd.DataFrame: Historique des ruptures
        """
        df = self.get_inventory_data(product, period_days)
        
        if 'is_stockout' in df.columns:
            stockouts = df[df['is_stockout'] == 1].copy()
        else:
            stockouts = df[df['current_stock_level'] == 0].copy()
        
        return stockouts
    
    def get_sales_by_condition(self, product, period_days=90):
        """
        Analyse des ventes par conditions météo.
        
        Args:
            product: Nom du produit
            period_days: Période d'analyse
            
        Returns:
            pd.DataFrame: Ventes groupées par condition
        """
        df = self.get_inventory_data(product, period_days)
        
        if 'weather_condition' not in df.columns:
            return None
        
        sales_by_weather = df.groupby('weather_condition').agg({
            'daily_sold_units': ['sum', 'mean', 'count']
        }).round(2)
        
        sales_by_weather.columns = ['total_sales', 'avg_daily_sales', 'days']
        
        return sales_by_weather.reset_index()
    
    def get_promotion_impact(self, product, period_days=90):
        """
        Analyse l'impact des promotions sur les ventes.
        
        Args:
            product: Nom du produit
            period_days: Période d'analyse
            
        Returns:
            dict: Impact des promotions
        """
        df = self.get_inventory_data(product, period_days)
        
        if 'promotion_active' not in df.columns:
            return None
        
        with_promo = df[df['promotion_active'] == 1]
        without_promo = df[df['promotion_active'] == 0]
        
        if len(with_promo) == 0 or len(without_promo) == 0:
            return None
        
        impact = {
            'avg_sales_with_promo': with_promo['daily_sold_units'].mean(),
            'avg_sales_without_promo': without_promo['daily_sold_units'].mean(),
            'promo_days': len(with_promo),
            'regular_days': len(without_promo),
            'uplift_percent': ((with_promo['daily_sold_units'].mean() / 
                               without_promo['daily_sold_units'].mean() - 1) * 100)
        }
        
        return impact
    
    def search_records(self, filters):
        """
        Recherche des enregistrements selon des filtres.
        
        Args:
            filters: Dictionnaire de filtres {colonne: valeur}
            
        Returns:
            pd.DataFrame: Enregistrements filtrés
        """
        df = self.data.copy()
        
        for column, value in filters.items():
            if column in df.columns:
                if isinstance(value, (list, tuple)):
                    df = df[df[column].isin(value)]
                else:
                    df = df[df[column] == value]
        
        return df
    
    def get_summary_stats(self):
        """
        Génère un résumé statistique global.
        
        Returns:
            dict: Statistiques globales
        """
        summary = {
            'total_records': len(self.data),
            'total_products': self.data['Product type'].nunique(),
            'date_range': self.get_date_range(),
            'total_sales': self.data['daily_sold_units'].sum(),
            'avg_daily_sales': self.data['daily_sold_units'].mean(),
            'total_stock': self.data.groupby('Product type')['current_stock_level'].last().sum(),
            'stockout_incidents': (self.data['is_stockout'] == 1).sum() if 'is_stockout' in self.data.columns else 0
        }
        
        # Ajouter des stats supplémentaires si disponibles
        if 'Revenue generated' in self.data.columns:
            summary['total_revenue'] = self.data['Revenue generated'].sum()
        
        if 'daily_production_units' in self.data.columns:
            summary['total_production'] = self.data['daily_production_units'].sum()
        
        return summary
    
    def backup_data(self, filepath):
        """
        Sauvegarde les données dans un fichier CSV.
        
        Args:
            filepath: Chemin du fichier de sauvegarde
        """
        try:
            self.data.to_csv(filepath, index=False)
            print(f"✅ Données sauvegardées dans {filepath}")
        except Exception as e:
            print(f"❌ Erreur de sauvegarde: {e}")
    
    def get_low_stock_products(self, threshold_days=7):
        """
        Identifie les produits avec un stock faible.
        
        Args:
            threshold_days: Nombre de jours de stock minimum
            
        Returns:
            list: Liste des produits en stock faible
        """
        low_stock = []
        
        for product in self.get_all_products():
            stats = self.get_product_stats(product, period_days=30)
            
            if stats and stats['avg_daily_sales'] > 0:
                days_of_stock = stats['current_stock'] / stats['avg_daily_sales']
                
                if days_of_stock < threshold_days:
                    low_stock.append({
                        'product': product,
                        'current_stock': stats['current_stock'],
                        'days_of_stock': round(days_of_stock, 1),
                        'avg_daily_sales': round(stats['avg_daily_sales'], 2)
                    })
        
        return sorted(low_stock, key=lambda x: x['days_of_stock'])
    
    def __repr__(self):
        """Représentation textuelle du gestionnaire."""
        return (f"DatabaseManager(records={len(self.data)}, "
                f"products={self.data['Product type'].nunique()}, "
                f"period={self.data['date'].min()} to {self.data['date'].max()})")
    
    def __len__(self):
        """Retourne le nombre d'enregistrements."""
        return len(self.data)