from datetime import datetime, timedelta
from sqlalchemy import func
from database_models import db
from database_models.user import User
from database_models.prediction import Prediction
from database_models.log import ActivityLog


def get_dashboard_statistics():
    """Retrieve full analytics statistics for Admin and User panels."""
    # Count totals
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    total_predictions = Prediction.query.count()
    fake_predictions = Prediction.query.filter_by(prediction='FAKE').count()
    real_predictions = Prediction.query.filter_by(prediction='REAL').count()

    # Calculate average confidence
    avg_confidence = db.session.query(func.avg(Prediction.confidence)).scalar() or 0.0
    avg_confidence = round(avg_confidence, 2)

    # Calculate average time
    avg_time = db.session.query(func.avg(Prediction.prediction_time)).scalar() or 0.0
    avg_time = round(avg_time, 4)

    # Get predictions count grouped by date for the last 7 days
    today = datetime.utcnow().date()
    daily_stats = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        daily_stats[day_str] = 0

    # Query daily counts from DB
    results = db.session.query(
        func.date(Prediction.created_at).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= datetime.utcnow() - timedelta(days=7)
    ).group_by(
        func.date(Prediction.created_at)
    ).all()

    for r in results:
        if r.date in daily_stats:
            daily_stats[r.date] = r.count
        else:
            # Handle potential string conversions of date
            date_str = str(r.date)
            if date_str in daily_stats:
                daily_stats[date_str] = r.count

    # Compile lists for charts
    chart_labels = list(daily_stats.keys())
    chart_data = list(daily_stats.values())

    # Get recent predictions
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()

    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_predictions': total_predictions,
        'fake_predictions': fake_predictions,
        'real_predictions': real_predictions,
        'avg_confidence': avg_confidence,
        'avg_time': avg_time,
        'daily_chart': {
            'labels': chart_labels,
            'data': chart_data
        },
        'recent': [p.to_dict() for p in recent_predictions]
    }


def get_user_statistics(user_id):
    """Retrieve statistics scoped to a single user ID."""
    total_predictions = Prediction.query.filter_by(user_id=user_id).count()
    fake_predictions = Prediction.query.filter_by(user_id=user_id, prediction='FAKE').count()
    real_predictions = Prediction.query.filter_by(user_id=user_id, prediction='REAL').count()

    avg_confidence = db.session.query(
        func.avg(Prediction.confidence)
    ).filter_by(user_id=user_id).scalar() or 0.0
    avg_confidence = round(avg_confidence, 2)

    # Get recent user predictions
    recent = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).limit(5).all()

    return {
        'total_predictions': total_predictions,
        'fake_predictions': fake_predictions,
        'real_predictions': real_predictions,
        'avg_confidence': avg_confidence,
        'recent': [p.to_dict() for p in recent]
    }
