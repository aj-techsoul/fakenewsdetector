"""
train_model.py — Train & Compare Models for Fake News AI
=========================================================
Trains 5 classifiers (Logistic Regression, Passive Aggressive, SVM,
Random Forest, Naive Bayes), compares metrics, selects the best model,
and saves vectorizer and metrics for dashboard reporting.
"""

import os
import pandas as pd
from ai.model_comparison import compare_and_train_models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
TRUE_CSV = os.path.join(DATASET_DIR, 'True.csv')
FAKE_CSV = os.path.join(DATASET_DIR, 'Fake.csv')

def generate_mock_if_missing():
    """Generates synthetic dataset if real dataset is not loaded yet."""
    if not os.path.exists(TRUE_CSV) or not os.path.exists(FAKE_CSV):
        print("\n⚠️  Dataset files not found. Auto-generating a small mock dataset for initial setup...")
        os.makedirs(DATASET_DIR, exist_ok=True)
        
        # Real News Synthetic dataset
        real_data = []
        for i in range(150):
            real_data.append({
                'title': f'U.S. Senate passes new economic growth budget bill {i}',
                'text': f'WASHINGTON (Reuters) - The U.S. Senate on Friday passed a sweeping bipartisan economic growth and budget bill following weeks of negotiations. The new legislation is expected to boost job creation and infrastructure development across the country. Official reports state that economists project a steady rise in employment rates as a result of the bill, representing a significant victory for the administration.',
                'subject': 'politicsNews',
                'date': 'July 17, 2026'
            })
        df_real_mock = pd.DataFrame(real_data)
        df_real_mock.to_csv(TRUE_CSV, index=False)

        # Fake News Synthetic dataset
        fake_data = []
        for i in range(150):
            fake_data.append({
                'title': f'BREAKING: Shocking secret chemical discovered in public water supply {i}!',
                'text': f'This is a major cover-up that the mainstream media won\'t tell you! A leaked report reveals that a secret government department has been adding an experimental chemical to public water reservoirs to control the population. Share this shocking truth with everyone you know before the big pharma companies and deep state take it down! Wake up people, this is a massive scandal!',
                'subject': 'Government',
                'date': 'July 17, 2026'
            })
        df_fake_mock = pd.DataFrame(fake_data)
        df_fake_mock.to_csv(FAKE_CSV, index=False)
        print("   ✅ Mock datasets generated successfully!")

if __name__ == '__main__':
    generate_mock_if_missing()
    compare_and_train_models(TRUE_CSV, FAKE_CSV, MODELS_DIR)
