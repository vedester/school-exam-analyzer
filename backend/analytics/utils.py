#backend/analytics/utils.py

import io
import zipfile
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# 1. DYNAMIC GRADING FUNCTION
def get_grade_details(score, scheme):
    """
    Loops through the user-defined scheme to find the grade.
    scheme = [{"min": 80, "max": 100, "grade": "EE", "remark": "...", "points": 4}, ...]
    Returns: (Grade, Remark, Points)
    """
    try:
        s = round(float(score))

    except (ValueError, TypeError):
        return "-", "", 0

    # Ensure scheme is a list
    if not isinstance(scheme, list):
        return "-", "Invalid Scheme", 0

    for rule in scheme:
        # Check if score falls in range
        try:
            if rule['min'] <= s <= rule['max']:
                return rule['grade'], rule['remark'], rule['points']
        except KeyError:
            continue
    
    return "-", "Not Graded", 0

def generate_student_reports(df, exam_instance):
    """
    Generates professional PDF report cards using dynamic settings.
    """
    zip_buffer = io.BytesIO()
       # 1. Get School Name
    try:
        school_name = exam_instance.uploaded_by.profile.school_name.upper()
    except:
        school_name = "KENYA SCHOOL ANALYTICS"
    
   # 2. Get Grading Scheme
    scheme = exam_instance.grading_scheme
    
    # Base exclusion list
     # 3. Detect Subjects (The Gatekeeper Logic - Keeps bad columns out)
    exclude_keywords = [
        'id', 'adm', 'admission', 'index', 'no.', 'number', 
        'name', 'student', 'phone', 'stream', 'gender', 'sex',
        'total', 'sum', 'average', 'avg', 'mean', 
        'rank', 'position', 'pos', 'grade', 'points', 'comment', 'remark',
        'overall grade', 'points'
    ]

    # Add User's Custom Ignore Columns
    if exam_instance.custom_ignore_columns:
        extras = [x.strip().lower() for x in exam_instance.custom_ignore_columns.split(',')]
        exclude_keywords.extend(extras)

    # Detect subjects for the PDF table
    
    subject_cols = []
    for col in df.columns:
        c_clean = col.lower().strip()
        if not any(k == c_clean or k in c_clean for k in exclude_keywords):
            # Double check if it looks numeric
            if pd.to_numeric(df[col], errors='coerce').notnull().sum() > 0:
                subject_cols.append(col)

 # 4. Detect Admission Column (The Detective Logic - Finds the Right ID)
    # We do this ONCE before the loop to save processing time
    adm_col_name = None
    
    # Priority 1: Strong clues (adm, reg, upi) - Catches "admision", "Adm No", "Reg"
    for col in df.columns:
        if any(x in col.lower() for x in ['adm', 'reg', 'upi']):
            adm_col_name = col
            break
            
    # Priority 2: Weak clues (index, id) - Only if Priority 1 failed
    if not adm_col_name:
        for col in df.columns:
            if any(x in col.lower() for x in ['index', 'student id', 'unique']):
                adm_col_name = col
                break


    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        for index, row in df.iterrows():
            pdf_buffer = io.BytesIO()
            p = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            
            # --- HEADER ---
            p.setFont("Helvetica-Bold", 18)
            p.drawCentredString(width / 2, height - 50, school_name) 
            
            p.setFont("Helvetica-Bold", 12)
            p.drawCentredString(width / 2, height - 75, "COMPETENCY BASED ASSESSMENT")
            p.drawCentredString(width / 2, height - 95, exam_instance.title)
            
            p.setLineWidth(2)
            p.line(30, height - 105, width - 30, height - 105)

            # --- STUDENT DETAILS ---
            student_name = str(row.get('Name', row.get('name', f'Student {index+1}'))).upper()
            rank = int(row.get('Rank', 0))
            
            # Safely get totals/averages
            try: total_score = float(row.get('Total', 0))
            except: total_score = 0.0
            
            try: avg_score = float(row.get('Average', 0))
            except: avg_score = 0.0
                
            overall_grade = row.get('Overall Grade', '-')

            # # Find Admission Number safely
            # adm = "N/A"
            # for k in ['Adm', 'adm', 'Admission', 'admission', 'Index']:
            #     if k in df.columns:
            #         adm = row[k]
            #         break
             # --- USE DETECTED ADMISSION COLUMN ---
            if adm_col_name:
                raw_adm = row.get(adm_col_name, "N/A")
                # Remove decimals (e.g., 4344.0 -> 4344)
                adm = str(raw_adm).split('.')[0]
            else:
                adm = "N/A"

            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, height - 140, f"NAME: {student_name}")
            p.drawString(50, height - 160, f"ADM NO: {adm}")
            
            p.drawString(350, height - 140, f"POSITION: {rank} / {len(df)}")
            p.drawString(350, height - 160, f"PERFORMANCE: {overall_grade}")

            # --- RESULTS TABLE ---
            y = height - 200
            
            # Table Headers
            p.setFillColor(colors.lightgrey)
            p.rect(50, y-5, 500, 20, fill=True, stroke=False)
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 10)
            p.drawString(60, y, "SUBJECT")
            p.drawString(250, y, "SCORE")
            p.drawString(330, y, "LEVEL")
            p.drawString(400, y, "REMARK")
            
            y -= 25
            p.setFont("Helvetica", 10)

            for subject in subject_cols:
                raw_score = row.get(subject, 0)
                try:
                    score = float(raw_score)
                except (ValueError, TypeError):
                    score = 0.0

                # USE DYNAMIC GRADING
                grade, remark, points = get_grade_details(score, scheme)
                
                p.drawString(60, y, str(subject).title())
                p.drawString(250, y, f"{score:.0f}") 
                p.drawString(330, y, grade)
                p.drawString(400, y, remark)
                
                p.setLineWidth(0.5)
                p.setStrokeColor(colors.lightgrey)
                p.line(50, y-5, 550, y-5)
                y -= 20

            # --- FOOTER SUMMARY ---
            y -= 30
            p.setStrokeColor(colors.black)
            p.setLineWidth(1)
            p.rect(50, y-40, 500, 40)
            p.setFont("Helvetica-Bold", 12)
            
            p.drawString(60, y-25, f"TOTAL: {total_score:.0f}")
            p.drawString(200, y-25, f"AVERAGE: {avg_score:.2f}")
            p.drawString(400, y-25, f"LEVEL: {overall_grade}")

            p.setFont("Helvetica-Oblique", 8)
            p.drawCentredString(width/2, 30, "Generated by School Analytics System")
            
            p.showPage()
            p.save()

            pdf_buffer.seek(0)
            clean_name = "".join([c for c in student_name if c.isalnum() or c==' ']).strip()
            zip_file.writestr(f"{rank}_{clean_name}.pdf", pdf_buffer.read())

    zip_buffer.seek(0)
    return zip_buffer