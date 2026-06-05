import os
import io
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from config import EXPORTS_DIR

def generate_pdf_report(user, profile, food_logs, water_logs, progress_logs):
    """
    Generate a beautiful health summary PDF report using ReportLab.
    Returns the file path of the saved PDF.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"NutriAI_Report_{user['username']}_{timestamp}.pdf"
    filepath = EXPORTS_DIR / filename
    
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0f172a") # Dark Slate
    c_secondary = colors.HexColor("#0284c7") # Ocean Blue
    c_text = colors.HexColor("#334155")
    c_light = colors.HexColor("#f8fafc")
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        alignment=0, # Left
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_text,
        spaceAfter=8
    )
    
    bold_body_style = ParagraphStyle(
        'DocBoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []
    
    # Header Branding
    story.append(Paragraph("NutriAI - Health & Nutrition Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 1. Profile Summary Section
    story.append(Paragraph("User Profile Summary", heading_style))
    
    height = profile.get('height', 0.0)
    weight = profile.get('weight', 0.0)
    height_m = height / 100.0
    bmi = round(weight / (height_m ** 2), 1) if height_m > 0 else 0.0
    
    profile_data = [
        [Paragraph("Full Name", bold_body_style), Paragraph(user['name'], body_style),
         Paragraph("Username", bold_body_style), Paragraph(user['username'], body_style)],
        [Paragraph("Age", bold_body_style), Paragraph(f"{profile.get('age')} years", body_style),
         Paragraph("Gender", bold_body_style), Paragraph(profile.get('gender'), body_style)],
        [Paragraph("Height", bold_body_style), Paragraph(f"{height} cm", body_style),
         Paragraph("Weight", bold_body_style), Paragraph(f"{weight} kg", body_style)],
        [Paragraph("BMI", bold_body_style), Paragraph(f"{bmi}", body_style),
         Paragraph("Fitness Goal", bold_body_style), Paragraph(profile.get('goal'), body_style)],
        [Paragraph("Activity Level", bold_body_style), Paragraph(profile.get('activity_level'), body_style),
         Paragraph("Diet Preference", bold_body_style), Paragraph(profile.get('dietary_preferences'), body_style)]
    ]
    
    t_profile = Table(profile_data, colWidths=[1.2*inch, 2.0*inch, 1.2*inch, 2.0*inch])
    t_profile.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(t_profile)
    story.append(Spacer(1, 20))
    
    # 2. Nutrition Logs Section
    story.append(Paragraph("Recent Nutrition & Food Logs", heading_style))
    if food_logs:
        food_headers = ["Date", "Meal Type", "Food Item", "Calories", "Protein", "Carbs", "Fat"]
        food_table_data = [[Paragraph(h, bold_body_style) for h in food_headers]]
        
        for log in food_logs[-10:]: # Limit to 10 entries for length
            row = [
                Paragraph(log['log_date'], body_style),
                Paragraph(log['meal_type'], body_style),
                Paragraph(log['food_name'], body_style),
                Paragraph(f"{int(log['calories'])} kcal", body_style),
                Paragraph(f"{int(log['protein'])}g", body_style),
                Paragraph(f"{int(log['carbs'])}g", body_style),
                Paragraph(f"{int(log['fat'])}g", body_style),
            ]
            food_table_data.append(row)
            
        t_food = Table(food_table_data, colWidths=[1.0*inch, 1.0*inch, 2.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        t_food.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ]))
        story.append(t_food)
    else:
        story.append(Paragraph("No recent food logs recorded.", body_style))
        
    story.append(Spacer(1, 20))
    
    # 3. Water and Health Progress Summary
    story.append(Paragraph("Hydration & Weight Tracker", heading_style))
    
    water_summary = f"Total logged days: {len(water_logs)}. "
    if water_logs:
        avg_water = sum([w.get('total_ml', w.get('intake_ml', 0)) for w in water_logs]) / len(water_logs)
        water_summary += f"Average daily water intake: {round(avg_water, 0)} ml."
    else:
        water_summary += "No water logs logged recently."
    story.append(Paragraph(water_summary, body_style))
    story.append(Spacer(1, 8))
    
    if progress_logs:
        progress_headers = ["Date", "Weight", "BMI", "Health Score"]
        prog_table_data = [[Paragraph(h, bold_body_style) for h in progress_headers]]
        for prog in progress_logs[-5:]:
            row = [
                Paragraph(prog['log_date'], body_style),
                Paragraph(f"{prog['weight']} kg", body_style),
                Paragraph(f"{prog['bmi']}", body_style),
                Paragraph(f"{int(prog['health_score'])}/100", body_style),
            ]
            prog_table_data.append(row)
            
        t_prog = Table(prog_table_data, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 1.6*inch])
        t_prog.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_prog)
    else:
        story.append(Paragraph("No progress history logs recorded.", body_style))
        
    story.append(Spacer(1, 30))
    
    # Disclaimer / Footer Info
    story.append(Paragraph("<i>Disclaimer: NutriAI provides health predictions and suggestions based on algorithms and general guidelines. Always consult with a qualified medical professional or registered dietitian for personalized healthcare advice.</i>", ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.HexColor("#64748b"))))
    
    # Build Document
    doc.build(story)
    return str(filepath)

def generate_csv_export(logs_list, columns_mapping=None):
    """
    Convert a list of log dictionaries to a downloadable CSV byte stream.
    """
    if not logs_list:
        return None
    
    df = pd.DataFrame(logs_list)
    if columns_mapping:
        df = df.rename(columns=columns_mapping)
        
    # Remove technical database keys if they exist
    for col in ['id', 'user_id', 'password_hash']:
        if col in df.columns:
            df = df.drop(columns=[col])
            
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode('utf-8')
