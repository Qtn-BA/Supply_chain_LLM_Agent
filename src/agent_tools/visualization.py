"""
Outils de visualisation des données
"""
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta

class Visualizer:
    """Gestionnaire de visualisations pour la supply chain."""
    
    def __init__(self, db_manager, analysis_engine):
        """
        Initialise le visualiseur.
        
        Args:
            db_manager: Instance de DatabaseManager
            analysis_engine: Instance d'AnalysisEngine
        """
        self.db = db_manager
        self.analysis = analysis_engine
        
        # Configuration du style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 100
    
    def plot_inventory_levels(self, product, days=30, save_path=None):
        """
        Visualise l'évolution des stocks.
        
        Args:
            product: Nom du produit
            days: Nombre de jours à afficher
            save_path: Chemin pour sauvegarder le graphique
        """
        df = self.db.get_inventory_data(product, period_days=days)
        
        if len(df) == 0:
            print(f"❌ Pas de données pour {product}")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        
        # Graphique des stocks
        ax1.plot(df['date'], df['current_stock_level'], 
                label='Niveau de stock', linewidth=2, color='#3b82f6')
        ax1.fill_between(df['date'], df['current_stock_level'], 
                         alpha=0.3, color='#3b82f6')
        ax1.set_title(f'Évolution du Stock - {product} 🤗', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Stock (unités)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Graphique des ventes
        ax2.bar(df['date'], df['daily_sold_units'], 
               label='Ventes quotidiennes', color='#10b981', alpha=0.7)
        ax2.set_title('Ventes Quotidiennes', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Unités vendues', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_demand_forecast(self, product, horizon=14, method='hf_enhanced', save_path=None):
        """
        Compare prévisions et ventes réelles.
        
        Args:
            product: Nom du produit
            horizon: Nombre de jours à prévoir
            method: Méthode de prévision
            save_path: Chemin pour sauvegarder le graphique
        """
        historical = self.db.get_inventory_data(product, period_days=30)
        forecast = self.analysis.forecast_demand(product, horizon, method)
        
        if forecast is None:
            return
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Ventes réelles
        ax.plot(historical['date'], historical['daily_sold_units'], 
               label='Ventes réelles', linewidth=2, color='#3b82f6', marker='o')
        
        # Prévisions
        ax.plot(forecast['date'], forecast['predicted_demand'], 
               label=f'Prévisions ({forecast["method"].iloc[0]})', linewidth=2, 
               color='#8b5cf6', linestyle='--', marker='s')
        
        # Intervalle de confiance
        ax.fill_between(forecast['date'], 
                       forecast['lower_bound'], 
                       forecast['upper_bound'],
                       alpha=0.2, color='#8b5cf6', label='Intervalle de confiance')
        
        ax.set_title(f'Prévisions de Demande - {product} 🤗', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Unités', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_anomalies(self, product=None, save_path=None):
        """
        Met en évidence les anomalies détectées.
        
        Args:
            product: Produit à analyser (None pour tous)
            save_path: Chemin pour sauvegarder le graphique
        """
        df = self.db.get_inventory_data(product, period_days=60)
        anomalies = self.analysis.detect_stock_anomalies(product)
        
        if anomalies is None or len(anomalies) == 0:
            print("Aucune anomalie à afficher")
            return
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Ligne de stock
        ax.plot(df['date'], df['current_stock_level'], 
               linewidth=2, color='#3b82f6', label='Stock')
        
        # Marqueurs d'anomalies
        severity_colors = {
            'critical': '#ef4444',
            'danger': '#f97316',
            'warning': '#eab308'
        }
        
        for severity, color in severity_colors.items():
            anom = anomalies[anomalies['severity'] == severity]
            if len(anom) > 0:
                ax.scatter(anom['date'], anom['stock_level'], 
                          s=150, color=color, marker='X', 
                          label=f'{severity.capitalize()}', zorder=5, 
                          edgecolors='black', linewidths=1.5)
        
        ax.set_title('Détection des Anomalies de Stock 🤗', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Niveau de stock', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_product_comparison(self, products=None, metric='daily_sold_units', save_path=None):
        """
        Compare plusieurs produits.
        
        Args:
            products: Liste de produits (None pour top 5)
            metric: Métrique à comparer
            save_path: Chemin pour sauvegarder
        """
        if products is None:
            all_products = self.db.get_all_products()
            products = all_products[:5]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for product in products:
            df = self.db.get_inventory_data(product, period_days=30)
            if len(df) > 0:
                ax.plot(df['date'], df[metric], label=product, linewidth=2, marker='o')
        
        ax.set_title(f'Comparaison des Produits - {metric}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_restock_urgency(self, restock_plan, save_path=None):
        """
        Visualise les urgences de réapprovisionnement.
        
        Args:
            restock_plan: DataFrame du plan de réappro
            save_path: Chemin pour sauvegarder
        """
        urgency_colors = {
            'urgent': '#ef4444',
            'high': '#f97316',
            'normal': '#10b981',
            'low': '#3b82f6'
        }
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Trier par jours de stock
        plot_data = restock_plan.sort_values('days_of_stock').head(15)
        
        colors = [urgency_colors.get(u, '#gray') for u in plot_data['urgency']]
        
        ax.barh(plot_data['product'], plot_data['days_of_stock'], color=colors)
        ax.set_xlabel('Jours de stock restants', fontsize=12)
        ax.set_title('Urgence de Réapprovisionnement par Produit', 
                    fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Légende
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=urg.capitalize()) 
                          for urg, color in urgency_colors.items()]
        ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Graphique sauvegardé: {save_path}")
        
        plt.show()