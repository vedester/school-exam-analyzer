# backend/analytics/analysis.pyadmin

import pandas as pd
import numpy as np
from django.core.files.base import ContentFile
from io import BytesIO
import traceback

# Import our helper modules
from .visualizer import subject_performance_chart, pass_rate_chart
from .utils import generate_student_reports, get_grade_details

def process_exam_file(exam_instance):
    try:
        # --- 1. READ FILE ---
        file_path = exam_instance.file.path
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # --- 2. DYNAMIC COLUMN DETECTION ---
        df.columns = df.columns.str.strip() 
        
        # Base metadata (Always ignored)
        metadata_keywords = [
            'id', 'adm', 'admission', 'index', 'name', 'phone', 'stream', 'gender', 'sex', 
            'total', 'pos', 'rank', 'dev', 'grade', 'points', 'kcpe', 'upi', 'number'
        ]
        
        # APPEND USER'S CUSTOM IGNORE COLUMNS (The Safety Valve)
        if exam_instance.custom_ignore_columns:
            # Convert string "UPI, Nemis" -> list ['upi', 'nemis']
            extras = [x.strip().lower() for x in exam_instance.custom_ignore_columns.split(',')]
            metadata_keywords.extend(extras)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Determine Subjects
        subject_cols = []
        for col in numeric_cols:
            c_lower = col.lower()
            # If the column name matches ANY keyword in the list, ignore it
            if not any(k in c_lower for k in metadata_keywords):
                subject_cols.append(col)
        
        if not subject_cols:
            raise ValueError(f"No subjects detected. Ignored columns containing: {metadata_keywords}")

        # --- 3. CALCULATIONS ---
        df[subject_cols] = df[subject_cols].fillna(0)
        df['Total'] = df[subject_cols].sum(axis=1)
        df['Average'] = df['Total'] / len(subject_cols)
        
        # --- 4. APPLY DYNAMIC GRADING ---
        scheme = exam_instance.grading_scheme # <--- Get JSON from DB

        def apply_grade_logic(row):
            # This returns (Grade, Remark, Points)
            g, r, p = get_grade_details(row['Average'], scheme)
            # We only want Grade and Points for the dataframe columns
            return pd.Series([g, p])

        # Create new columns based on the Average
        df[['Overall Grade', 'Points']] = df.apply(apply_grade_logic, axis=1)
        
        # Ranking
        df['Rank'] = df['Total'].rank(ascending=False, method='min')
        df = df.sort_values(by='Rank')

        # --- 5. PREPARE DASHBOARD METADATA ---
        subject_means = df[subject_cols].mean().sort_values(ascending=False)
        # --- FIX STARTS HERE: Smart Name Detection ---
        best_student_name = "Unknown"
        
        # List of possible headers for the student name
        name_candidates = ['name', 'student', 'student name', 'names', 'full name']
        
        # Loop through columns to find the one that contains the name
        for col in df.columns:
            if col.lower().strip() in name_candidates:
                # We found the name column!
                # Since df is sorted by Rank, iloc[0] is the top student
                best_student_name = str(df.iloc[0][col])
                break
        # --- FIX ENDS HERE ---
        # Count Pass Rate based on "ME" (Meeting Expectations) threshold (usually 50)
        # We can find the threshold dynamically from the scheme if needed, defaulting to 50
        pass_threshold = 50
        
        summary_stats = {
            "student_count": len(df),
            "class_mean": round(df['Average'].mean(), 2),
            "top_student": best_student_name.title(), 
            "top_score": float(df.iloc[0]['Total']),
            "pass_rate": round((len(df[df['Average'] >= pass_threshold]) / len(df)) * 100, 1),
            "best_subject": subject_means.index[0] if not subject_means.empty else "N/A",
            "worst_subject": subject_means.index[-1] if not subject_means.empty else "N/A"
        }
        
        exam_instance.analysis_summary = summary_stats
        
        # --- 6. SAVE EXCEL ---
        output_io = BytesIO()
        with pd.ExcelWriter(output_io, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Broadsheet', index=False)
            
            sub_analysis = pd.DataFrame({
                'Mean': subject_means, 
                'Highest': df[subject_cols].max(),
                'Lowest': df[subject_cols].min()
            })
            sub_analysis.to_excel(writer, sheet_name='Subject Analysis')
            
        output_io.seek(0)
        exam_instance.processed_file.save(f"Analyzed_{exam_instance.title}.xlsx", ContentFile(output_io.read()), save=False)

        # --- 7. CHARTS ---
        try:
            sub_means_df = subject_means.reset_index()
            sub_means_df.columns = ['Subject', 'Mean Score']
            c1 = subject_performance_chart(sub_means_df)
            exam_instance.subject_chart.save(f"sub_chart.png", ContentFile(c1.read()), save=False)

            c2 = pass_rate_chart(df)
            exam_instance.passrate_chart.save(f"pass_chart.png", ContentFile(c2.read()), save=False)
        except Exception as e:
            print(f"Chart Error: {e}")

        # --- 8. PDF REPORTS ---
        try:
            # Pass the WHOLE exam_instance so utils can access grading_scheme
            zip_buffer = generate_student_reports(df, exam_instance)
            exam_instance.reports_zip.save(f"Reports.zip", ContentFile(zip_buffer.read()), save=False)
        except Exception as e:
            print(f"Report Error: {e}")
            traceback.print_exc() # Print full error to console for debugging

        # --- 9. FINISH ---
        exam_instance.status = 'COMPLETED'
        exam_instance.message = "Analysis completed successfully."
        exam_instance.save()

    except Exception as e:
        exam_instance.status = 'FAILED'
        exam_instance.message = f"Error: {str(e)}"
        print(f"CRITICAL ERROR: {traceback.format_exc()}")
        exam_instance.save()