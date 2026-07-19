import os
from datetime import datetime
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)


class PremiumReportPDF(FPDF):
    """Corporate-style PDF generation class with Header, Footer and Page borders."""
    
    def header(self):
        # Top branding header
        self.set_fill_color(12, 12, 29) # Dark Midnight background
        self.rect(0, 0, 210, 24, 'F')
        
        self.set_y(6)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 6, ' FAKEGUARD AI ', align='L', new_x='LMARGIN', new_y='NEXT')
        
        self.set_y(6)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(162, 155, 254)
        self.cell(0, 6, 'Enterprise News Verification System', align='R', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(12)

    def footer(self):
        # Bottom page footer
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        # Border separation line
        self.line(10, 280, 200, 280)
        
        self.cell(100, 10, 'CONFIDENTIAL — FakeGuard AI Verification Report', align='L')
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='R')


def generate_premium_pdf_report(prediction_dict):
    """
    Generate an enterprise-quality PDF report for a prediction record.
    """
    pdf = PremiumReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    # ─── Title & Info Panel ───────────────────────────────────────────
    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(45, 52, 54)
    pdf.cell(0, 8, 'Prediction Classification Report', new_x='LMARGIN', new_y='NEXT')
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Analysis timestamp: {prediction_dict.get('created_at') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
             new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # ─── Classification Status Badge ──────────────────────────────────
    label = prediction_dict.get('prediction', 'UNKNOWN')
    confidence = prediction_dict.get('confidence', 0)
    reliability = prediction_dict.get('reliability', 'N/A')
    risk_category = prediction_dict.get('risk_category', 'N/A')
    ai_score = prediction_dict.get('ai_score', 0.0)

    # Color definitions
    if label == 'REAL':
        pdf.set_fill_color(0, 184, 148)  # Green
        badge_text = 'REAL NEWS'
    else:
        pdf.set_fill_color(225, 112, 85) # Red
        badge_text = 'FAKE NEWS'

    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    
    badge_width = pdf.get_string_width(badge_text) + 24
    x_centered = (210 - badge_width) / 2
    pdf.set_x(x_centered)
    pdf.cell(badge_width, 14, badge_text, fill=True, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(6)

    # ─── Metrics Matrix ───────────────────────────────────────────────
    pdf.set_fill_color(248, 249, 250)
    pdf.rect(10, pdf.get_y(), 190, 32, 'F')
    
    pdf.set_text_color(45, 52, 54)
    pdf.set_y(pdf.get_y() + 4)
    
    # Grid columns
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(47, 5, 'CONFIDENCE', align='C', new_x='END')
    pdf.cell(47, 5, 'RELIABILITY INDEX', align='C', new_x='END')
    pdf.cell(47, 5, 'RISK PROFILE', align='C', new_x='END')
    pdf.cell(47, 5, 'AI QUALITY SCORE', align='C', new_x='LMARGIN', new_y='NEXT')
    
    pdf.ln(1)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(47, 8, f"{confidence}%", align='C', new_x='END')
    pdf.cell(47, 8, reliability, align='C', new_x='END')
    pdf.cell(47, 8, risk_category, align='C', new_x='END')
    pdf.cell(47, 8, f"{ai_score}/10", align='C', new_x='LMARGIN', new_y='NEXT')
    
    pdf.ln(8)

    # ─── AI Explainable Reasons ───────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(108, 92, 231)  # Royal Purple Accent
    pdf.cell(0, 6, 'Explainable AI Analysis Output', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(60, 60, 60)
    explanation = prediction_dict.get('explanation', '')
    clean_explanation = explanation.replace('**', '')
    pdf.multi_cell(0, 5, clean_explanation)
    pdf.ln(4)

    # ─── Linguistic statistics ────────────────────────────────────────
    stats = prediction_dict.get('stats', {})
    if stats:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(108, 92, 231)
        pdf.cell(0, 6, 'Text Quality & NLP Statistics', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        # Draw mini-grid for statistics
        pdf.set_font('Helvetica', '', 9)
        stat_rows = [
            [('Word Count', stats.get('word_count', 0)), ('Readability Score', stats.get('readability_score', 0))],
            [('Sentence Count', stats.get('sentence_count', 0)), ('Readability Level', stats.get('readability_label', 'N/A'))],
            [('Lexical Richness', f"{stats.get('vocab_richness', 0)}%"), ('Content Spam Index', f"{stats.get('spam_score', 0)}/100")]
        ]
        
        for row in stat_rows:
            # Col 1
            pdf.set_text_color(128, 128, 128)
            pdf.cell(40, 5, row[0][0] + ':', new_x='END')
            pdf.set_text_color(45, 52, 54)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(50, 5, str(row[0][1]), new_x='END')
            
            # Col 2
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(45, 5, row[1][0] + ':', new_x='END')
            pdf.set_text_color(45, 52, 54)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 5, str(row[1][1]), new_x='LMARGIN', new_y='NEXT')
            
            pdf.set_font('Helvetica', '', 9)
            
        pdf.ln(6)

    # ─── Article Keywords ─────────────────────────────────────────────
    keywords = prediction_dict.get('keywords', {})
    if keywords and any(keywords.values()):
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(108, 92, 231)
        pdf.cell(0, 6, 'Key Term Categorization', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        labels_map = {
            'positive': 'Credible References',
            'negative': 'Sensational Clues',
            'suspicious': 'Subjective Phrases',
            'repeated': 'Clickbait Phrases'
        }

        pdf.set_font('Helvetica', '', 9)
        for key, text_lbl in labels_map.items():
            words_list = keywords.get(key, [])
            if words_list:
                pdf.set_text_color(128, 128, 128)
                pdf.cell(45, 5, text_lbl + ':', new_x='END')
                pdf.set_text_color(45, 52, 54)
                pdf.cell(0, 5, ', '.join(words_list), new_x='LMARGIN', new_y='NEXT')
        pdf.ln(6)

    # ─── Article Preview Snippet ──────────────────────────────────────
    preview = prediction_dict.get('text_preview', '') or prediction_dict.get('full_text', '')[:300]
    if preview:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(108, 92, 231)
        pdf.cell(0, 6, 'Source Text Excerpt', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)
        
        pdf.set_font('Helvetica', 'I', 9.5)
        pdf.set_text_color(110, 110, 110)
        # safe ascii encoding
        preview_clean = preview.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 4.5, f'"{preview_clean}..."')

    # ─── Save Document ────────────────────────────────────────────────
    record_id = prediction_dict.get('id', 'temp')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"report_{record_id}_{timestamp}.pdf"
    file_path = os.path.join(REPORTS_DIR, filename)

    pdf.output(file_path)
    return file_path
