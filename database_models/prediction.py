import json
from datetime import datetime
from database_models import db

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    text_preview = db.Column(db.String(255), nullable=False)
    full_text = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.String(10), nullable=False)  # 'REAL' or 'FAKE'
    confidence = db.Column(db.Float, nullable=False)
    fake_prob = db.Column(db.Float, nullable=False)
    real_prob = db.Column(db.Float, nullable=False)
    reliability = db.Column(db.String(20), nullable=False)  # 'Very High', 'High', etc.
    risk_category = db.Column(db.String(20), nullable=False)  # 'Very Low', 'High', etc.
    ai_score = db.Column(db.Float, nullable=False)  # 0.0 to 10.0
    explanation = db.Column(db.Text, nullable=False)
    keywords_json = db.Column(db.Text, nullable=False)  # JSON serialized keywords lists
    stats_json = db.Column(db.Text, nullable=False)  # JSON serialized text statistics
    prediction_time = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_keywords(self):
        try:
            return json.loads(self.keywords_json)
        except Exception:
            return {}

    def get_stats(self):
        try:
            return json.loads(self.stats_json)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'text_preview': self.text_preview,
            'full_text': self.full_text,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'fake_prob': self.fake_prob,
            'real_prob': self.real_prob,
            'reliability': self.reliability,
            'risk_category': self.risk_category,
            'ai_score': self.ai_score,
            'explanation': self.explanation,
            'keywords': self.get_keywords(),
            'stats': self.get_stats(),
            'prediction_time': self.prediction_time,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
