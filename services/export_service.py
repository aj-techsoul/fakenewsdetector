import csv
import io
from datetime import datetime

def export_predictions_to_csv(prediction_list):
    """
    Compile a list of prediction dictionary records into a CSV file format.
    
    Returns:
        StringIO stream containing the full CSV output.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        'Prediction ID', 'User ID', 'Date Created', 'Prediction', 
        'Confidence (%)', 'Fake Probability (%)', 'Real Probability (%)',
        'Reliability Level', 'Risk Category', 'AI Score (/10)', 
        'Speed (seconds)', 'Text Preview', 'AI Explanation'
    ])

    for p in prediction_list:
        writer.writerow([
            p.get('id'),
            p.get('user_id') or 'Anonymous',
            p.get('created_at'),
            p.get('prediction'),
            p.get('confidence'),
            p.get('fake_prob'),
            p.get('real_prob'),
            p.get('reliability'),
            p.get('risk_category'),
            p.get('ai_score'),
            p.get('prediction_time'),
            p.get('text_preview', '').replace('\n', ' '),
            p.get('explanation', '').replace('\n', ' ')
        ])

    output.seek(0)
    return output
