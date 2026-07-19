"""
backend/report_generator.py — PDF Report Generator
====================================================
Generates professional PDF reports for prediction results
using the fpdf2 library.
"""

import os
from datetime import datetime
from fpdf import FPDF


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)


class ReportPDF(FPDF):
    """Custom PDF class with header and footer."""

    def header(self):
        """Page header with project title."""
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(41, 128, 185)
        self.cell(0, 10, 'Fake News Detection Report', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'AI-Powered News Analysis System', align='C', new_x='LMARGIN', new_y='NEXT')
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(8)

    def footer(self):
        """Page footer with page number and date."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')


def generate_report(prediction_data):
    """
    Generate a PDF report for a prediction result.

    Args:
        prediction_data: dict containing prediction details

    Returns:
        str: Path to the generated PDF file
    """
    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ─── Prediction Result Section ────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, 'Prediction Result', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    label = prediction_data.get('prediction', 'UNKNOWN')
    confidence = prediction_data.get('confidence', 0)

    # Prediction badge
    if label == 'REAL':
        pdf.set_fill_color(39, 174, 96)
        badge_text = 'REAL NEWS'
    else:
        pdf.set_fill_color(231, 76, 60)
        badge_text = 'FAKE NEWS'

    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(255, 255, 255)
    badge_width = pdf.get_string_width(badge_text) + 20
    x_pos = (210 - badge_width) / 2
    pdf.set_x(x_pos)
    pdf.cell(badge_width, 14, badge_text, fill=True, align='C',
             new_x='LMARGIN', new_y='NEXT')
    pdf.ln(8)

    # ─── Confidence & Metrics ─────────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 8, 'Analysis Metrics', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    metrics = [
        ('Confidence', f'{confidence}%'),
        ('Fake Probability', f'{prediction_data.get("fake_prob", 0)}%'),
        ('Real Probability', f'{prediction_data.get("real_prob", 0)}%'),
        ('Prediction Time', f'{prediction_data.get("prediction_time", 0)}s'),
        ('Analysis Date', prediction_data.get('created_at',
                                               datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    ]

    pdf.set_font('Helvetica', '', 10)
    for metric_name, metric_value in metrics:
        pdf.set_text_color(100, 100, 100)
        pdf.cell(60, 7, metric_name + ':', new_x='END')
        pdf.set_text_color(44, 62, 80)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 7, str(metric_value), new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Helvetica', '', 10)

    pdf.ln(5)

    # ─── AI Explanation ───────────────────────────────────────────────
    explanation = prediction_data.get('explanation', '')
    if explanation:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 8, 'AI Explanation', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(60, 60, 60)
        # Clean markdown bold markers for PDF
        clean_explanation = explanation.replace('**', '')
        pdf.multi_cell(0, 6, clean_explanation)
        pdf.ln(5)

    # ─── Text Statistics ──────────────────────────────────────────────
    stats = prediction_data.get('stats', {})
    if stats:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 8, 'Text Statistics', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        stat_items = [
            ('Word Count', stats.get('word_count', 0)),
            ('Character Count', stats.get('char_count', 0)),
            ('Sentence Count', stats.get('sentence_count', 0)),
            ('Reading Time', stats.get('reading_time', 'N/A')),
            ('Avg Word Length', stats.get('avg_word_length', 0)),
            ('Vocabulary Richness', f'{stats.get("vocabulary_richness", 0)}%'),
            ('Complexity Score', f'{stats.get("complexity_score", 0)}/100'),
            ('Spam Score', f'{stats.get("spam_score", 0)}/100'),
        ]

        pdf.set_font('Helvetica', '', 10)
        for stat_name, stat_value in stat_items:
            pdf.set_text_color(100, 100, 100)
            pdf.cell(60, 7, stat_name + ':', new_x='END')
            pdf.set_text_color(44, 62, 80)
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 7, str(stat_value), new_x='LMARGIN', new_y='NEXT')
            pdf.set_font('Helvetica', '', 10)

        pdf.ln(5)

    # ─── Keywords ─────────────────────────────────────────────────────
    keywords = prediction_data.get('keywords', {})
    if keywords and any(keywords.values()):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 8, 'Keyword Analysis', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        keyword_labels = {
            'positive': 'Credibility Indicators',
            'negative': 'Sensational Words',
            'suspicious': 'Suspicious Phrases',
            'emotional': 'Emotional Words',
            'repeated': 'Frequently Repeated'
        }

        pdf.set_font('Helvetica', '', 10)
        for key, display_label in keyword_labels.items():
            words_list = keywords.get(key, [])
            if words_list:
                pdf.set_text_color(100, 100, 100)
                pdf.cell(55, 7, display_label + ':', new_x='END')
                pdf.set_text_color(44, 62, 80)
                pdf.cell(0, 7, ', '.join(words_list), new_x='LMARGIN', new_y='NEXT')

        pdf.ln(5)

    # ─── Article Preview ──────────────────────────────────────────────
    text_preview = prediction_data.get('text_preview', '') or \
                   prediction_data.get('full_text', '')[:500]
    if text_preview:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 8, 'Article Preview', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(80, 80, 80)
        # Encode text safely for PDF
        safe_text = text_preview[:500].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, safe_text + ('...' if len(text_preview) > 500 else ''))

    # ─── Save PDF ─────────────────────────────────────────────────────
    prediction_id = prediction_data.get('id', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'report_{prediction_id}_{timestamp}.pdf'
    filepath = os.path.join(REPORTS_DIR, filename)

    pdf.output(filepath)

    return filepath
