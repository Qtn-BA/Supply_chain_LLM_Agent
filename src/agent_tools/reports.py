"""
Outils de génération de rapports
"""
from datetime import datetime
import pandas as pd

class ReportGenerator:
    """Générateur de rapports d'analyse supply chain."""
    
    def __init__(self, db_manager, analysis_engine):
        """
        Initialise le générateur de rapports.
        
        Args:
            db_manager: Instance de DatabaseManager
            analysis_engine: Instance d'AnalysisEngine
        """
        self.db = db_manager
        self.analysis = analysis_engine
    
    def generate_inventory_report(self, output_file='supply_chain_report_hf.txt'):
        """
        Crée un rapport complet d'analyse avec Hugging Face.
        
        Args:
            output_file: Nom du fichier de sortie
            
        Returns:
            str: Contenu du rapport
        """
        print("\n" + "="*60)
        print("📊 GÉNÉRATION DU RAPPORT D'ANALYSE SUPPLY CHAIN (HF)")
        print("="*60 + "\n")
        
        report_lines = []
        report_lines.append("="*60)
        report_lines.append("RAPPORT D'ANALYSE SUPPLY CHAIN 🤗 HUGGING FACE")
        report_lines.append("="*60)
        report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        date_range = self.db.get_date_range()
        report_lines.append(f"Période: {date_range['start']} à {date_range['end']}")
        report_lines.append("")
        
        # Statistiques générales
        report_lines.extend(self._generate_general_stats())
        
        # Analyse par produit
        report_lines.extend(self._generate_product_analysis())
        
        # Anomalies
        report_lines.extend(self._generate_anomaly_report())
        
        # Plan de réapprovisionnement
        report_lines.extend(self._generate_restock_report())
        
        # Footer
        report_lines.append("\n💡 POWERED BY HUGGING FACE 🤗")
        report_lines.append("="*60)
        
        report_text = "\n".join(report_lines)
        print(report_text)
        
        # Sauvegarder
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n✅ Rapport sauvegardé: {output_file}")
        return report_text
    
    def _generate_general_stats(self):
        """Génère les statistiques générales."""
        lines = []
        lines.append("📈 STATISTIQUES GÉNÉRALES")
        lines.append("-" * 60)
        
        data = self.db.data
        lines.append(f"Enregistrements: {len(data)}")
        lines.append(f"Produits: {data['Product type'].nunique()}")
        lines.append(f"Ventes totales: {data['daily_sold_units'].sum():.0f} unités")
        lines.append(f"Stock total: {data.groupby('Product type')['current_stock_level'].last().sum():.0f} unités")
        lines.append("")
        
        return lines
    
    def _generate_product_analysis(self):
        """Génère l'analyse par produit."""
        lines = []
        lines.append("📦 ANALYSE PAR PRODUIT (avec sentiment HF)")
        lines.append("-" * 60)
        
        products = self.db.get_all_products()[:3]
        
        for product in products:
            stats = self.db.get_product_stats(product, period_days=30)
            
            if stats:
                lines.append(f"\n{product}:")
                lines.append(f"  • Ventes (30j): {stats['total_sales']:.0f} unités")
                lines.append(f"  • Ventes moy/jour: {stats['avg_daily_sales']:.2f} unités")
                lines.append(f"  • Stock actuel: {stats['current_stock']:.0f} unités")
                
                # Analyse de sentiment HF
                sentiment = self.analysis.analyze_market_sentiment(product)
                if sentiment:
                    lines.append(f"  • 🤗 Sentiment: {sentiment['label']} ({sentiment['score']:.2%})")
        
        lines.append("")
        return lines
    
    def _generate_anomaly_report(self):
        """Génère le rapport des anomalies."""
        lines = []
        lines.append("\n⚠️ ANOMALIES DÉTECTÉES (avec classification HF)")
        lines.append("-" * 60)
        
        all_anomalies = self.analysis.detect_stock_anomalies()
        
        if all_anomalies is not None and len(all_anomalies) > 0:
            lines.append(f"Total: {len(all_anomalies)} anomalies")
            
            for _, anom in all_anomalies.head(5).iterrows():
                lines.append(f"\n  • {anom['date'].strftime('%Y-%m-%d')} - {anom['product']}:")
                lines.append(f"    {anom['type']} - {anom['message']}")
                if 'hf_category' in anom and pd.notna(anom['hf_category']):
                    lines.append(f"    🤗 Catégorie HF: {anom['hf_category']}")
        else:
            lines.append("✅ Aucune anomalie détectée")
        
        lines.append("")
        return lines
    
    def _generate_restock_report(self):
        """Génère le plan de réapprovisionnement."""
        lines = []
        lines.append("\n📋 PLAN DE RÉAPPROVISIONNEMENT (avec IA)")
        lines.append("-" * 60)
        
        restock = self.analysis.suggest_restock_plan()
        urgent = restock[restock['urgency'].isin(['urgent', 'high'])]
        
        if len(urgent) > 0:
            lines.append(f"⚠️ {len(urgent)} produits nécessitent une action:\n")
            
            for _, item in urgent.head(3).iterrows():
                lines.append(f"  • {item['product']}:")
                lines.append(f"    - Stock: {item['current_stock']} unités")
                lines.append(f"    - Action: {item['action']}")
                lines.append(f"    - Qté suggérée: {item['suggested_order_qty']} unités")
                
                if 'ai_recommendation' in item and pd.notna(item['ai_recommendation']):
                    lines.append(f"    - 🤗 IA: {item['ai_recommendation'][:100]}...")
        else:
            lines.append("✅ Niveaux satisfaisants")
        
        lines.append("")
        return lines
    
    def generate_product_report(self, product, output_file=None):
        """
        Génère un rapport détaillé pour un produit.
        
        Args:
            product: Nom du produit
            output_file: Nom du fichier de sortie
            
        Returns:
            str: Contenu du rapport
        """
        lines = []
        lines.append("="*60)
        lines.append(f"RAPPORT DÉTAILLÉ - {product}")
        lines.append("="*60)
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Statistiques
        stats = self.db.get_product_stats(product, period_days=30)
        if stats:
            lines.append("📊 STATISTIQUES (30 derniers jours)")
            lines.append("-" * 60)
            lines.append(f"Ventes totales: {stats['total_sales']:.0f} unités")
            lines.append(f"Ventes moyennes/jour: {stats['avg_daily_sales']:.2f} unités")
            lines.append(f"Stock actuel: {stats['current_stock']:.0f} unités")
            lines.append(f"Stock minimum: {stats['min_stock']:.0f} unités")
            lines.append(f"Stock maximum: {stats['max_stock']:.0f} unités")
            lines.append(f"Jours de rupture: {stats['stockout_days']}")
            lines.append("")
        
        # Prévisions
        lines.append("🔮 PRÉVISIONS (14 jours)")
        lines.append("-" * 60)
        forecast = self.analysis.forecast_demand(product, horizon=14)
        if forecast is not None:
            total_forecast = forecast['predicted_demand'].sum()
            lines.append(f"Demande prévue totale: {total_forecast:.0f} unités")
            lines.append(f"Demande moyenne/jour: {total_forecast/14:.2f} unités")
            lines.append(f"Méthode: {forecast['method'].iloc[0]}")
        lines.append("")
        
        # Anomalies
        lines.append("⚠️ ANOMALIES")
        lines.append("-" * 60)
        anomalies = self.analysis.detect_stock_anomalies(product)
        if anomalies is not None and len(anomalies) > 0:
            lines.append(f"Total: {len(anomalies)} anomalies détectées")
            for _, anom in anomalies.head(3).iterrows():
                lines.append(f"  • {anom['date'].strftime('%Y-%m-%d')}: {anom['message']}")
        else:
            lines.append("✅ Aucune anomalie")
        
        lines.append("")
        lines.append("="*60)
        
        report_text = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Rapport produit sauvegardé: {output_file}")
        
        return report_text
    
    def generate_summary_stats(self):
        """Génère un résumé statistique rapide."""
        data = self.db.data
        date_range = self.db.get_date_range()
        
        summary = {
            'total_records': len(data),
            'total_products': data['Product type'].nunique(),
            'date_range': f"{date_range['start']} à {date_range['end']}",
            'total_sales': data['daily_sold_units'].sum(),
            'avg_daily_sales': data['daily_sold_units'].mean(),
            'total_stock': data.groupby('Product type')['current_stock_level'].last().sum(),
            'stockout_incidents': (data['is_stockout'] == 1).sum()
        }
        
        return summary