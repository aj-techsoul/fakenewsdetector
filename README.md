# 🔍 FakeGuard AI — Professional Enterprise Fake News Detection Platform

FakeGuard AI is a production-quality, enterprise-grade web application that leverages advanced natural language processing (NLP), text lemmatization, and machine learning to analyze news articles and classify them as **Real** or **Fake** with detailed confidence metrics and Explainable AI (XAI) details.

---

## 🚀 Key Upgraded Features

- 🤖 **Advanced AI Engine** — Replaces simple stems with WordNet Lemmatization, NFC Unicode normalizations, emoji/html tag scrubs, and sentiment pattern comparison.
- 📊 **Multimodel Comparison** — Trains 5 classifiers (Logistic Regression, Linear SVM, Passive Aggressive, Random Forest, Naive Bayes), automatically selects the highest performer, and outputs comparative statistics.
- 🎨 **Theme Engine** — Features 5 premium visual styles (Midnight Blue, Emerald Green, Royal Purple, Sunset Orange, Crimson Red) that update CSS variables dynamically.
- 🔒 **Enterprise Security** — Custom rate limiting decorators, XSS tags filters, and database parameterized queries via SQLAlchemy.
- 👤 **Role-Based Auth** — Secure login/register portals with distinct user workspaces and admin management control centers.
- 📈 **Stats Dashboard** — High-fidelity analytics monitoring active user logs, daily predictions, and dataset ROC curves.
- 📄 **Premium PDFs** — Formatted analysis reports using FPDF2 and exportable spreadsheet logs.

---

## 🛠️ Technology Stack

| Layer | Component |
|---|---|
| **Backend** | Python 3, Flask, Flask-Login, Flask-SQLAlchemy |
| **Security** | BCrypt, IP Rate Limiting, Input Sanitization |
| **NLP Pipeline** | NLTK (Stopwords, WordNet Lemmatizer, VADER Sentiment) |
| **ML Engine** | Scikit-learn (Logistic Regression, PA, SVM, RF, MNB, TF-IDF 1-3 Grams) |
| **Database** | SQLite |
| **Frontend** | HTML5, CSS3 Variables, ES6 JavaScript, Chart.js, Font Awesome 6 |

---

## 📂 Project Reorganized Structure

```
fake-news-ai/
├── app.py                      # Flask factory application setup
├── train_model.py              # ML pipeline trigger (model comparison)
├── requirements.txt            # Python package dependencies
├── README.md                   # This documentation guide
│
├── database/                   # SQLite databases folder
├── dataset/                    # Training CSV files (True.csv / Fake.csv)
├── models/                     # Trained models, vectorizers, and evaluation metrics
├── reports/                    # Generated PDF prediction reports
├── uploads/                    # Profile avatars uploads
├── exports/                    # CSV spreadsheet logs
├── logs/                       # Server-side logs
├── backups/                    # Database backup storage
│
├── database_models/            # SQLAlchemy schemas
│   ├── __init__.py             # db ORM initialization
│   ├── user.py                 # User and Admin schema
│   ├── prediction.py           # NLP Prediction logs schema
│   ├── log.py                  # User audit logs schema
│   ├── notification.py         # Push alerts schema
│   └── setting.py              # Admin configurations schema
│
├── authentication/             # Security blueprints
│   ├── __init__.py             
│   ├── auth.py                 # Blueprints routes (login, register, profiles)
│   └── security.py             # BCrypt hashes, XSS filters, Rate limiters
│
├── ai/                         # Machine learning models
│   ├── __init__.py             
│   ├── preprocessor.py         # Lemmatizer and NFC unicode text cleaner
│   ├── feature_engineering.py  # Flesch readability, sentiment polarity
│   ├── model_comparison.py     # Evaluation across 5 classifiers
│   └── predictor.py            # AI prediction, clickbait highlighter
│
├── analytics/                  # Stats aggregator
│   ├── stats_service.py        # Analytics trends queries
│   └── __init__.py             
│
├── services/                   # Export utilities
│   ├── __init__.py             
│   ├── report_service.py       # PDF document compiling
│   ├── export_service.py       # CSV spreadsheet exporter
│   └── notification_service.py # System pushes and toast triggers
│
├── utils/                      # Route helpers
│   ├── __init__.py             
│   └── helpers.py              # admin_required decorators
│
├── templates/                  # Jinja2 layouts
│   ├── base.html               # Nav, responsive sidebar, bells dropdown
│   ├── index.html              # Landing page (FAQs, testimonials, pipeline)
│   ├── login.html              # Auth Login
│   ├── register.html           # Auth Register
│   ├── dashboard.html          # User workspace (editor + viewer)
│   ├── admin.html              # Admin panel control
│   ├── profile.html            # Profile changes, password, logs
│   ├── settings.html           # Theme selector palettes
│   └── error.html              # Custom error pages
│
└── static/                     # Assets folder
    ├── css/
    │   └── style.css           # Glassmorphism & layouts style sheets
    ├── js/
    │   ├── main.js             # Sidebar actions & toast triggers
    │   ├── auth.js             # Password strength updates
    │   ├── workspace.js        # Predict AJAX workspace logic
    │   ├── result.js           # Static reports chart/highlight renders
    │   └── admin.js            # User actions & retrain trigger JS
    └── themes/
        └── theme-engine.js     # Live theme updates switcher
```

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- pip

### Step 1: Clone and Navigate
```bash
cd d:\fakenews_detection
```

### Step 2: Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # MacOS/Linux
```

### Step 3: Install Packages
```bash
pip install -r requirements.txt
```

### Step 4: Dataset Placement
- To use the real dataset, download the **ISOT Fake and Real News Dataset** from [Kaggle](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset).
- Place `True.csv` and `Fake.csv` inside the `dataset/` directory.
- *If you do not have the files yet, the pipeline will auto-generate a synthetic mock dataset of 300 news articles on first launch so that you can verify features out-of-the-box!*

### Step 5: Train Models
Run the comparative model training script:
```bash
python train_model.py
```
This trains Logistic Regression, PA, SVM, Random Forest, and Naive Bayes, prints F1-scores, saves the highest-performing model to `models/model.pkl`, and writes performance metrics.

### Step 6: Start Application
```bash
python app.py
```
Access the dashboard workspace at: **http://localhost:5000**

---

## 📖 User Guide

### Access Credentials
Out-of-the-box, the database is pre-seeded with a default administrator account:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@fakeguard.ai`

Users can register new accounts using the registration form.

### How to Scan News
1. Go to the **Workspace Dashboard**.
2. Click **Sample Real** or **Sample Fake** to populate sample texts, or paste an article.
3. Click **Execute Verification**.
4. Review the results:
   - **Linguistic Highlight Viewer**: Hover over colored terms in the text reader to view markers (Caps, Clickbait, Sensational).
   - **XAI Reasonings**: Read bullet points detailing why the text matches real/fake news.
   - **Linguistic Indices**: View word counts, spam scores, and reading difficulty.
   - **Report PDF**: Click the PDF button to download a formatted summary sheet.

---

## ⚙️ Administrator Guide

### User Profiles Admin Actions
On the **Admin Control Panel**:
- **Suspend/Activate**: Temporarily disable user accounts. Disabled users cannot log in.
- **Delete Account**: Permanently wipe a user record (also deletes linked logs/predictions).

### Retraining Pipeline
- Clicking **Trigger Pipeline Retraining** runs evaluations across the 5 models asynchronously, automatically updates the active predictor files, and reloads metrics.

### Exports
- Click **Export Database Logs CSV** to download a spreadsheet record of prediction history.

---

## 🔒 Security Configuration

1. **Brute Force Limiting**: Integrates a `@rate_limit(limit=10, period_seconds=60)` decorator on authorization pathways. Exceeding requests returns a `429 Rate Limit` card.
2. **SQLi Prevention**: SQLAlchemy ORM query methods run parameterized statements, eliminating raw string concatenations.
3. **XSS Protection**: Inputs are scrubbed using HTML tags replacement regex prior to execution or storage.

---

## 🛠️ Future Improvements
- **Live Scrapers**: Add URL inputs that automatically scrape and scan pages.
- **Deep Learning Fallbacks**: Integrate Transformer models (e.g. DistilBERT) for deep semantic analysis.
- **Factor Auditing**: Connect to fact-checking databases (e.g. Politifact API) to audit specific named entities.
