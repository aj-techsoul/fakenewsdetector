import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc

from ai.preprocessor import clean_text_nlp

def compare_and_train_models(true_csv, fake_csv, models_dir):
    """
    Load dataset, clean texts, vectorize using TF-IDF (1-3 n-grams),
    train 5 classifiers, select the best model, and save metrics.
    """
    start_time = time.time()
    os.makedirs(models_dir, exist_ok=True)

    print("📖 Loading datasets for comparison training...")
    df_true = pd.read_csv(true_csv)
    df_fake = pd.read_csv(fake_csv)

    df_true['label'] = 1
    df_fake['label'] = 0

    df = pd.concat([df_true, df_fake], axis=0, ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df['combined'] = df['title'].fillna('') + ' ' + df['text'].fillna('')

    print(f"🧹 Preprocessing {len(df)} texts using Lemmatizer...")
    df['cleaned'] = df['combined'].apply(clean_text_nlp)
    df = df[df['cleaned'].str.len() > 0].reset_index(drop=True)

    print("📐 Feature extraction with TF-IDF (N-grams: 1 to 3)...")
    vectorizer = TfidfVectorizer(max_df=0.7, max_features=40000, ngram_range=(1, 3))
    X = vectorizer.fit_transform(df['cleaned'])
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Models definition with optimized parameters
    classifiers = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
        'Passive Aggressive': PassiveAggressiveClassifier(max_iter=100, random_state=42, early_stopping=True),
        'Linear SVM': LinearSVC(random_state=42, max_iter=2000, dual='auto'),
        'Random Forest': RandomForestClassifier(n_estimators=30, random_state=42, n_jobs=-1),
        'Naive Bayes': MultinomialNB()
    }

    comparison_results = []
    best_f1 = -1
    best_model_name = None
    best_model = None

    print("🤖 Evaluating multiple classifiers...")
    for name, clf in classifiers.items():
        t_start = time.time()
        clf.fit(X_train, y_train)
        train_time = time.time() - t_start

        y_pred = clf.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='binary')
        rec = recall_score(y_test, y_pred, average='binary')
        f1 = f1_score(y_test, y_pred, average='binary')

        print(f"   📊 {name} -> Accuracy: {acc*100:.2f}%, F1-Score: {f1*100:.2f}% (Trained in {train_time:.2f}s)")

        comparison_results.append({
            'model_name': name,
            'accuracy': round(acc * 100, 2),
            'precision': round(prec * 100, 2),
            'recall': round(rec * 100, 2),
            'f1_score': round(f1 * 100, 2),
            'training_time': round(train_time, 2)
        })

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = clf

    print(f"\n🏆 Best Model Selected: {best_model_name} with F1-Score: {best_f1*100:.2f}%")

    # Evaluate best model thoroughly for dashboard
    y_pred_best = best_model.predict(X_test)
    
    # Check if decision_function is available (SVM/PA/LR)
    try:
        y_scores = best_model.decision_function(X_test)
    except AttributeError:
        # Fallback for Random Forest / Naive Bayes (use predict_proba)
        try:
            y_scores = best_model.predict_proba(X_test)[:, 1]
        except Exception:
            y_scores = np.zeros(len(y_test))

    fpr, tpr, _ = roc_curve(y_test, y_scores)
    roc_auc = auc(fpr, tpr)
    cm = confusion_matrix(y_test, y_pred_best)

    # Save outputs
    print("💾 Saving best model and vectorizer...")
    joblib.dump(best_model, os.path.join(models_dir, 'model.pkl'))
    joblib.dump(vectorizer, os.path.join(models_dir, 'vectorizer.pkl'))

    metrics = {
        'model_name': best_model_name,
        'dataset_name': 'ISOT Real and Fake News',
        'total_articles': len(df),
        'real_count': int((y == 1).sum()),
        'fake_count': int((y == 0).sum()),
        'train_samples': X_train.shape[0],
        'test_samples': X_test.shape[0],
        'vocabulary_size': len(vectorizer.vocabulary_),
        'testing_accuracy': round(accuracy_score(y_test, y_pred_best) * 100, 2),
        'precision': round(precision_score(y_test, y_pred_best) * 100, 2),
        'recall': round(recall_score(y_test, y_pred_best) * 100, 2),
        'f1_score': round(best_f1 * 100, 2),
        'roc_auc': round(roc_auc, 4),
        'confusion_matrix': cm.tolist(),
        'comparison': comparison_results,
        'total_pipeline_time': round(time.time() - start_time, 2),
        'roc_curve': {
            'fpr': [round(float(x), 4) for x in fpr.tolist()],
            'tpr': [round(float(x), 4) for x in tpr.tolist()]
        }
    }

    with open(os.path.join(models_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    print("✅ Model selection training complete!")
    return metrics
