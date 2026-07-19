import io
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for, current_app
from flask_login import login_required, current_user

from database_models import db
from database_models.user import User
from database_models.prediction import Prediction
from database_models.log import ActivityLog
from database_models.notification import Notification
from database_models.setting import Setting

from ai.predictor import predict_news_article, load_predictor
from ai.model_comparison import compare_and_train_models
from analytics.stats_service import get_dashboard_statistics, get_user_statistics
from services.report_service import generate_premium_pdf_report
from services.export_service import export_predictions_to_csv
from services.notification_service import create_user_notification, get_user_notifications, mark_notifications_read
from utils.helpers import admin_required
from authentication.security import sanitize_input_text

main_bp = Blueprint('main', __name__)

# Sample news constants
SAMPLE_REAL_NEWS = (
    "WASHINGTON (Reuters) - The U.S. labor market remained tight in November, with the economy "
    "adding 228,000 jobs, exceeding economists' predictions. The unemployment rate hovered around "
    "4.1%, the lowest index in 17 years. Positive growth was observed in manufacturing and healthcare "
    "sectors. Federal Reserve officials confirmed that the strong employment index supports their "
    "upcoming monetary policy projections."
)

SAMPLE_FAKE_NEWS = (
    "BREAKING: Shocking leak from a secret government department reveals a hidden agenda to add chemical "
    "substances to city water reserves! Doctors warn that this compound is being used to manipulate "
    "population thoughts. Big Pharma companies and deep state networks have completely suppressed this truth "
    "for decades. Share this shocking truth widely before they delete this post!"
)


@main_bp.route('/')
def index():
    """System Landing page."""
    # Retrieve model training metrics if available
    metrics_path = os.path.join(current_app.root_path, 'models', 'metrics.json')
    metrics = None
    if os.path.exists(metrics_path):
        import json
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception:
            pass
            
    return render_template('index.html', metrics=metrics)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User analysis workspace dashboard."""
    user_stats = get_user_statistics(current_user.id)
    return render_template('dashboard.html', 
                           stats=user_stats, 
                           sample_real=SAMPLE_REAL_NEWS, 
                           sample_fake=SAMPLE_FAKE_NEWS)


@main_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    """API endpoint to analyze text and save results."""
    data = request.get_json() or {}
    raw_text = data.get('text', '').strip()

    if not raw_text or len(raw_text) < 30:
        return jsonify({'error': 'Article text must be at least 30 characters.'}), 400

    try:
        # Run prediction pipeline
        res = predict_news_article(raw_text)

        # Save to database prediction record
        import json
        new_pred = Prediction(
            user_id=current_user.id,
            text_preview=raw_text[:120],
            full_text=raw_text,
            prediction=res['label'],
            confidence=res['confidence'],
            fake_prob=res['fake_prob'],
            real_prob=res['real_prob'],
            reliability=res['reliability'],
            risk_category=res['risk_category'],
            ai_score=res['ai_score'],
            explanation=res['explanation'],
            keywords_json=json.dumps(res['keywords']),
            stats_json=json.dumps(res['stats']),
            prediction_time=res['prediction_time']
        )
        db.session.add(new_pred)
        db.session.commit()

        # Send user notification alert
        create_user_notification(
            user_id=current_user.id,
            title="Prediction Completed",
            message=f"Verified article as {res['label']} ({res['confidence']}% confidence).",
            type='success' if res['label'] == 'REAL' else 'warning'
        )

        # Add to response dict
        res['id'] = new_pred.id
        return jsonify(res)

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Verification pipeline failed: {str(e)}"}), 500


@main_bp.route('/result/<int:pred_id>')
@login_required
def result(pred_id):
    """View analysis verification report details."""
    pred = Prediction.query.get_or_40004 = Prediction.query.filter_by(id=pred_id).first_or_404()
    
    # Security check: User can only view their own predictions unless Admin
    if pred.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
        
    return render_template('result.html', data=pred.to_dict())


@main_bp.route('/history')
@login_required
def history():
    """Prediction scan history logs."""
    # Query parameters
    search = sanitize_input_text(request.args.get('search', ''))
    prediction_filter = request.args.get('prediction', 'all')
    sort_by = request.args.get('sort', 'date_desc')

    query = Prediction.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(Prediction.full_text.like(f"%{search}%"))

    if prediction_filter == 'real':
        query = query.filter_by(prediction='REAL')
    elif prediction_filter == 'fake':
        query = query.filter_by(prediction='FAKE')

    # Sorting
    if sort_by == 'date_asc':
        query = query.order_by(Prediction.created_at.asc())
    elif sort_by == 'confidence_desc':
        query = query.order_by(Prediction.confidence.desc())
    elif sort_by == 'confidence_asc':
        query = query.order_by(Prediction.confidence.asc())
    else:
        # Default newest first
        query = query.order_by(Prediction.created_at.desc())

    predictions = query.all()
    return render_template('history.html', 
                           predictions=[p.to_dict() for p in predictions],
                           search=search,
                           prediction_filter=prediction_filter,
                           sort_by=sort_by)


@main_bp.route('/profile')
@login_required
def profile():
    """User profile management panel."""
    # Get user active logs
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    return render_template('profile.html', logs=logs)


@main_bp.route('/settings')
@login_required
def settings_page():
    """General settings view."""
    return render_template('settings.html')


# ─── Admin Blueprints ─────────────────────────────────────────────────────────

@main_bp.route('/admin')
@login_required
@admin_required
def admin():
    """Admin Dashboard Control Center."""
    stats = get_dashboard_statistics()
    users = User.query.order_by(User.created_at.desc()).all()
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(20).all()
    
    # Read metrics comparison details
    metrics_path = os.path.join(current_app.root_path, 'models', 'metrics.json')
    metrics = None
    if os.path.exists(metrics_path):
        import json
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception:
            pass

    return render_template('admin.html', 
                           stats=stats, 
                           users=users, 
                           logs=logs,
                           metrics=metrics)


@main_bp.route('/admin/users/<int:user_id>/action', methods=['POST'])
@login_required
@admin_required
def admin_user_action(user_id):
    """Suspend, activate, or delete accounts."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot perform administrative operations on your own session.'}), 400

    data = request.get_json() or {}
    action = data.get('action')

    if action == 'suspend':
        user.is_active = False
        action_desc = "Suspended user account"
    elif action == 'activate':
        user.is_active = True
        action_desc = "Activated user account"
    elif action == 'delete':
        db.session.delete(user)
        action_desc = "Deleted user account"
    else:
        return jsonify({'error': 'Unknown administrative action requested.'}), 400

    db.session.commit()

    # Log action
    log = ActivityLog(
        user_id=current_user.id,
        action=f"{action_desc}: {user.username}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'success': True, 'message': f"Operation '{action}' executed successfully."})


@main_bp.route('/admin/model/retrain', methods=['POST'])
@login_required
@admin_required
def admin_model_retrain():
    """Trigger model retraining comparison asynchronously."""
    true_csv = os.path.join(current_app.root_path, 'dataset', 'True.csv')
    fake_csv = os.path.join(current_app.root_path, 'dataset', 'Fake.csv')
    models_dir = os.path.join(current_app.root_path, 'models')

    if not os.path.exists(true_csv) or not os.path.exists(fake_csv):
        return jsonify({'error': 'True.csv or Fake.csv training datasets are missing.'}), 404

    try:
        metrics = compare_and_train_models(true_csv, fake_csv, models_dir)
        load_predictor()  # Reload the newly trained predictor into memory

        # Log action
        log = ActivityLog(
            user_id=current_user.id,
            action=f"Retrained models pipeline. Selected best: {metrics['model_name']} ({metrics['testing_accuracy']}% accuracy)",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()

        # Send alert
        create_user_notification(
            user_id=current_user.id,
            title="ML Model Re-trained",
            message=f"Model comparison completed. Best algorithm: {metrics['model_name']} ({metrics['testing_accuracy']}% test score).",
            type='success'
        )

        return jsonify({'success': True, 'metrics': metrics})

    except Exception as e:
        return jsonify({'error': f"Training failed: {str(e)}"}), 500


# ─── Documents & Exports ──────────────────────────────────────────────────────

@main_bp.route('/api/report/<int:pred_id>')
@login_required
def api_report(pred_id):
    """Compile PDF verification report and download."""
    pred = Prediction.query.get_or_404(pred_id)
    if pred.user_id != current_user.id and current_user.role != 'admin':
        abort(403)

    try:
        report_path = generate_premium_pdf_report(pred.to_dict())
        return send_file(report_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f"Could not compile document: {str(e)}"}), 500


@main_bp.route('/admin/export/csv')
@login_required
@admin_required
def admin_export_csv():
    """Export prediction databases for admin logs analysis."""
    preds = Prediction.query.order_by(Prediction.created_at.desc()).all()
    stream = export_predictions_to_csv([p.to_dict() for p in preds])
    
    return send_file(
        io.BytesIO(stream.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"all_predictions_export_{datetime.now().strftime('%Y%m%d')}.csv"
    )


# ─── Alert API Notifications ──────────────────────────────────────────────────

@main_bp.route('/api/notifications', methods=['GET'])
@login_required
def api_notifications():
    """Get active alerts lists."""
    notifs = get_user_notifications(current_user.id, only_unread=True)
    return jsonify({
        'notifications': [n.to_dict() for n in notifs]
    })


@main_bp.route('/api/notifications/read', methods=['POST'])
@login_required
def api_notifications_read():
    """Mark alerts as read."""
    mark_notifications_read(current_user.id)
    return jsonify({'success': True})
