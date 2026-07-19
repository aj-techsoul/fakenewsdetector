"""
backend/routes.py — Flask Routes & API Endpoints
==================================================
Defines all page routes and API endpoints for the
Fake News Detection System.
"""

import csv
import io
from flask import (
    Blueprint, render_template, request, jsonify, send_file, redirect, url_for
)
from backend.ml_model import (
    predict, generate_explanation, extract_keywords, get_metrics, is_model_loaded
)
from backend.text_analysis import analyze_text
from backend.database import (
    save_prediction, get_prediction, get_all_predictions,
    delete_prediction, delete_all_predictions, get_stats,
    get_prediction_count, get_all_for_export
)
from backend.report_generator import generate_report

# ─── Blueprint ───────────────────────────────────────────────────────────────

main = Blueprint('main', __name__)

# ─── Sample News Articles ────────────────────────────────────────────────────

SAMPLE_REAL_NEWS = """WASHINGTON (Reuters) - The U.S. economy added 228,000 jobs in November, the Labor Department reported on Friday, exceeding economists' expectations of 200,000 new positions. The unemployment rate held steady at 4.1 percent, the lowest level in 17 years. Average hourly earnings rose 0.2 percent, bringing the annual increase to 2.5 percent. The strong employment data reinforced expectations that the Federal Reserve would raise interest rates at its December meeting. The report showed broad-based gains across sectors, with professional and business services, manufacturing, and healthcare all contributing to job growth."""

SAMPLE_FAKE_NEWS = """BREAKING: Scientists have discovered that drinking coffee makes you immortal! A secret government study that was suppressed for decades has finally been leaked, revealing that coffee contains a miracle compound that reverses aging. Big Pharma has been hiding this information because it would destroy their billion-dollar anti-aging industry. Share this before they delete it! The mainstream media won't report this because they are controlled by pharmaceutical companies. Wake up people! This is the biggest cover-up in human history!"""


# ─── Page Routes ─────────────────────────────────────────────────────────────

@main.route('/')
def index():
    """Home dashboard / landing page."""
    stats = get_stats()
    return render_template('index.html', stats=stats)


@main.route('/analyze')
def analyze():
    """News analysis input page."""
    return render_template('analyze.html',
                           sample_real=SAMPLE_REAL_NEWS,
                           sample_fake=SAMPLE_FAKE_NEWS)


@main.route('/result/<int:prediction_id>')
def result(prediction_id):
    """Prediction result page."""
    prediction_data = get_prediction(prediction_id)
    if not prediction_data:
        return redirect(url_for('main.analyze'))
    return render_template('result.html', data=prediction_data)


@main.route('/history')
def history():
    """Prediction history page."""
    return render_template('history.html')


@main.route('/dataset')
def dataset_info():
    """Dataset information and model metrics page."""
    metrics = get_metrics()
    return render_template('dataset_info.html', metrics=metrics)


@main.route('/dashboard')
def dashboard():
    """Machine learning dashboard."""
    stats = get_stats()
    metrics = get_metrics()
    return render_template('dashboard.html', stats=stats, metrics=metrics)


@main.route('/admin')
def admin():
    """Admin panel."""
    stats = get_stats()
    return render_template('admin.html', stats=stats)


@main.route('/about')
def about():
    """About page."""
    return render_template('about.html')


# ─── API Routes ──────────────────────────────────────────────────────────────

@main.route('/predict', methods=['POST'])
def predict_news():
    """
    Run ML prediction on user-submitted text.

    Expects JSON: { "text": "..." }
    Returns JSON with prediction result, explanation, keywords, stats.
    """
    data = request.get_json()

    if not data or not data.get('text'):
        return jsonify({'error': 'No text provided'}), 400

    text = data['text'].strip()

    # Validation
    if len(text) < 20:
        return jsonify({
            'error': 'Text is too short. Please provide at least 20 characters.'
        }), 400

    if len(text.split()) < 5:
        return jsonify({
            'error': 'Text is too short. Please provide at least 5 words.'
        }), 400

    if not is_model_loaded():
        return jsonify({
            'error': 'Model not loaded. Please run train_model.py first.'
        }), 503

    try:
        # Run prediction
        prediction_result = predict(text)

        # Generate explanation
        explanation = generate_explanation(text, prediction_result)

        # Extract keywords
        keywords = extract_keywords(text)

        # Analyze text statistics
        stats = analyze_text(text)

        # Determine risk level
        confidence = prediction_result['confidence']
        if prediction_result['label'] == 'FAKE':
            if confidence >= 90:
                risk_level = 'Very High'
            elif confidence >= 75:
                risk_level = 'High'
            elif confidence >= 60:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
        else:
            if confidence >= 90:
                risk_level = 'Very Low'
            elif confidence >= 75:
                risk_level = 'Low'
            elif confidence >= 60:
                risk_level = 'Medium'
            else:
                risk_level = 'Moderate'

        # Save to database
        db_data = {
            'text_preview': text[:200],
            'full_text': text,
            'prediction': prediction_result['label'],
            'confidence': prediction_result['confidence'],
            'fake_prob': prediction_result['fake_prob'],
            'real_prob': prediction_result['real_prob'],
            'prediction_time': prediction_result['prediction_time'],
            'keywords': keywords,
            'stats': stats,
            'explanation': explanation
        }
        prediction_id = save_prediction(db_data)

        # Return response
        return jsonify({
            'id': prediction_id,
            'prediction': prediction_result['label'],
            'confidence': prediction_result['confidence'],
            'fake_prob': prediction_result['fake_prob'],
            'real_prob': prediction_result['real_prob'],
            'prediction_time': prediction_result['prediction_time'],
            'explanation': explanation,
            'keywords': keywords,
            'stats': stats,
            'risk_level': risk_level
        })

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@main.route('/api/history')
def api_history():
    """
    Get prediction history with search, filter, and sort.

    Query params: search, filter (all/real/fake), sort (date_desc, etc.), limit, offset
    """
    search = request.args.get('search', '')
    filter_type = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'date_desc')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    predictions = get_all_predictions(
        search=search,
        filter_type=filter_type,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )

    total = get_prediction_count()

    return jsonify({
        'predictions': predictions,
        'total': total
    })


@main.route('/api/history/<int:prediction_id>', methods=['DELETE'])
def api_delete_prediction(prediction_id):
    """Delete a single prediction."""
    delete_prediction(prediction_id)
    return jsonify({'success': True})


@main.route('/api/history/clear', methods=['DELETE'])
def api_clear_history():
    """Delete all predictions."""
    delete_all_predictions()
    return jsonify({'success': True})


@main.route('/api/history/export')
def api_export_csv():
    """Export all predictions as CSV."""
    predictions = get_all_for_export()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'ID', 'Date', 'Prediction', 'Confidence', 'Fake Probability',
        'Real Probability', 'Prediction Time', 'Text Preview', 'Explanation'
    ])

    # Data rows
    for p in predictions:
        writer.writerow([
            p.get('id'),
            p.get('created_at'),
            p.get('prediction'),
            p.get('confidence'),
            p.get('fake_prob'),
            p.get('real_prob'),
            p.get('prediction_time'),
            p.get('text_preview', '')[:100],
            p.get('explanation', '')[:200]
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='prediction_history.csv'
    )


@main.route('/api/report/<int:prediction_id>')
def api_generate_report(prediction_id):
    """Generate and download a PDF report for a prediction."""
    prediction_data = get_prediction(prediction_id)

    if not prediction_data:
        return jsonify({'error': 'Prediction not found'}), 404

    try:
        filepath = generate_report(prediction_data)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500


@main.route('/api/stats')
def api_stats():
    """Get global statistics for dashboard."""
    stats = get_stats()
    metrics = get_metrics()
    return jsonify({
        'stats': stats,
        'metrics': metrics
    })


@main.route('/api/sample-news')
def api_sample_news():
    """Get sample news articles."""
    return jsonify({
        'real': SAMPLE_REAL_NEWS,
        'fake': SAMPLE_FAKE_NEWS
    })
