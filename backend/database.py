"""
backend/database.py — SQLite Database Manager
===============================================
Handles all database operations for prediction history:
create, read, search, filter, delete, stats, and export.
"""

import os
import sqlite3
import json
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'predictions.db')


def get_db():
    """Get a database connection with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_preview TEXT NOT NULL,
            full_text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            fake_prob REAL NOT NULL,
            real_prob REAL NOT NULL,
            prediction_time REAL NOT NULL,
            keywords_json TEXT,
            stats_json TEXT,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ─── CRUD Operations ────────────────────────────────────────────────────────

def save_prediction(data):
    """
    Save a prediction result to the database.

    Args:
        data: dict with keys matching the predictions table columns

    Returns:
        int: The ID of the newly inserted record
    """
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO predictions
        (text_preview, full_text, prediction, confidence, fake_prob,
         real_prob, prediction_time, keywords_json, stats_json, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('text_preview', '')[:200],
        data.get('full_text', ''),
        data.get('prediction', ''),
        data.get('confidence', 0),
        data.get('fake_prob', 0),
        data.get('real_prob', 0),
        data.get('prediction_time', 0),
        json.dumps(data.get('keywords', {})),
        json.dumps(data.get('stats', {})),
        data.get('explanation', '')
    ))
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prediction_id


def get_prediction(prediction_id):
    """Get a single prediction by ID."""
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM predictions WHERE id = ?', (prediction_id,)
    ).fetchone()
    conn.close()

    if row:
        return _row_to_dict(row)
    return None


def get_all_predictions(search='', filter_type='all', sort_by='date_desc',
                        limit=50, offset=0):
    """
    Get all predictions with optional search, filter, and sort.

    Args:
        search: Search term for text_preview
        filter_type: 'all', 'real', or 'fake'
        sort_by: 'date_desc', 'date_asc', 'confidence_desc', 'confidence_asc'
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        list of prediction dicts
    """
    conn = get_db()
    query = 'SELECT * FROM predictions WHERE 1=1'
    params = []

    # Search filter
    if search:
        query += ' AND (text_preview LIKE ? OR explanation LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term])

    # Type filter
    if filter_type == 'real':
        query += ' AND prediction = ?'
        params.append('REAL')
    elif filter_type == 'fake':
        query += ' AND prediction = ?'
        params.append('FAKE')

    # Sorting
    sort_map = {
        'date_desc': 'created_at DESC',
        'date_asc': 'created_at ASC',
        'confidence_desc': 'confidence DESC',
        'confidence_asc': 'confidence ASC'
    }
    query += f' ORDER BY {sort_map.get(sort_by, "created_at DESC")}'

    # Pagination
    query += ' LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [_row_to_dict(row) for row in rows]


def delete_prediction(prediction_id):
    """Delete a prediction by ID."""
    conn = get_db()
    conn.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
    conn.commit()
    conn.close()
    return True


def delete_all_predictions():
    """Delete all predictions."""
    conn = get_db()
    conn.execute('DELETE FROM predictions')
    conn.commit()
    conn.close()
    return True


def get_prediction_count():
    """Get total number of predictions."""
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
    conn.close()
    return count


def get_stats():
    """Get aggregate statistics for the dashboard."""
    conn = get_db()

    total = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
    real_count = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE prediction = 'REAL'"
    ).fetchone()[0]
    fake_count = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE prediction = 'FAKE'"
    ).fetchone()[0]
    avg_confidence = conn.execute(
        'SELECT AVG(confidence) FROM predictions'
    ).fetchone()[0] or 0
    avg_time = conn.execute(
        'SELECT AVG(prediction_time) FROM predictions'
    ).fetchone()[0] or 0

    # Recent predictions
    recent = conn.execute(
        'SELECT * FROM predictions ORDER BY created_at DESC LIMIT 5'
    ).fetchall()

    conn.close()

    return {
        'total': total,
        'real_count': real_count,
        'fake_count': fake_count,
        'avg_confidence': round(avg_confidence, 2),
        'avg_time': round(avg_time, 4),
        'recent': [_row_to_dict(r) for r in recent]
    }


def get_all_for_export():
    """Get all predictions for CSV export."""
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM predictions ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return [_row_to_dict(row) for row in rows]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _row_to_dict(row):
    """Convert a sqlite3.Row to a dictionary, parsing JSON fields."""
    d = dict(row)

    # Parse JSON fields
    if d.get('keywords_json'):
        try:
            d['keywords'] = json.loads(d['keywords_json'])
        except (json.JSONDecodeError, TypeError):
            d['keywords'] = {}

    if d.get('stats_json'):
        try:
            d['stats'] = json.loads(d['stats_json'])
        except (json.JSONDecodeError, TypeError):
            d['stats'] = {}

    return d
