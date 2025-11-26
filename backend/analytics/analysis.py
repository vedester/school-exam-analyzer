# backend/analytics/analysis.py
import pandas as pd
import numpy as np
from django.core.files.base import ContentFile
from io import BytesIO
from .visualizer import subject_performance_chart, pass_rate_chart
from .utils import generate_student_reports 

def process_exam_file(exam_instance):
    try:
        file_path = exam_instance.file.path
        
        # 1. Read the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # 2. SMART COLUMN DETECTION (With Safety Fix)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # CRITICAL: Exclude 'Total', 'Rank', 'Average' to prevent re-upload errors
        exclude_keywords = [
            'id', 'adm', 'phone', 'contact', 'year', 'stream', 'class', 'age',
            'total', 'sum', 'average', 'avg', 'mean', 'rank', 'position'
        ]
        
        subject_cols = [
            col for col in numeric_cols 
            if not any(k in col.lower() for k in exclude_keywords)
        ]
        
        if not subject_cols:
            raise ValueError("No subjects detected. Please check column names.")

        # 3. CALCULATIONS
        df[subject_cols] = df[subject_cols].fillna(0)
        df['Total'] = df[subject_cols].sum(axis=1)
        df['Average'] = df['Total'] / len(subject_cols)
        df['Rank'] = df['Total'].rank(ascending=False, method='min')
        df = df.sort_values(by='Rank')

        # 4. PREPARE DATA FOR VISUALIZER
        subject_means = df[subject_cols].mean().reset_index()
        subject_means.columns = ['Subject', 'Mean Score']
        
        best_subject_row = subject_means.loc[subject_means['Mean Score'].idxmax()]
        
        # Summary for Excel
        summary_data = {
            'Metric': ['Class Mean Total', 'Best Subject', 'Best Subject Mean'],
            'Value': [df['Total'].mean(), best_subject_row['Subject'], best_subject_row['Mean Score']]
        }
        summary_df = pd.DataFrame(summary_data)

        # 5. SAVE EXCEL RESULT
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Student Ranks', index=False)
            subject_means.to_excel(writer, sheet_name='Subject Performance', index=False)
            summary_df.to_excel(writer, sheet_name='Overview', index=False)

        output.seek(0)
        filename = f"Results_{exam_instance.title}.xlsx"
        exam_instance.processed_file.save(filename, ContentFile(output.read()), save=False)

        # 6. GENERATE & SAVE CHARTS (The Fixed Part)
        try:
            # Generate Chart 1 (Pass the means dataframe)
            chart1_buffer = subject_performance_chart(subject_means)
            exam_instance.subject_chart.save(
                f"{exam_instance.title}_subject_chart.png",
                ContentFile(chart1_buffer.read()), # Read directly from the returned buffer
                save=False
            )

            # Generate Chart 2 (Pass the full dataframe)
            chart2_buffer = pass_rate_chart(df)
            exam_instance.passrate_chart.save(
                f"{exam_instance.title}_passrate_chart.png",
                ContentFile(chart2_buffer.read()), # Read directly from the returned buffer
                save=False
            )
            
        except Exception as chart_error:
            print(f"Chart generation failed: {chart_error}")
            # We don't stop the process if charts fail, just log it.

        # 7. UPDATE STATUS
        exam_instance.status = 'COMPLETED'
        exam_instance.message = (
            f"Analysis Ready! \n"
            f"Best Subject: {best_subject_row['Subject']} ({best_subject_row['Mean Score']:.1f})"
        )
        exam_instance.save()
        print("Results generated successfully.")

        try:

            print("Generating PDF reports...")
            zip_buffer = generate_student_reports(df, exam_instance.title)
                
            filename = f"Reports_{exam_instance.title}.zip"
            exam_instance.reports_zip.save(filename, ContentFile(zip_buffer.read()), save=False)
            print("PDF reports generated.")
        except Exception as pdf_error:
                print(f"PDF Generation failed: {pdf_error}")
            
    except Exception as e:
        exam_instance.status = 'FAILED'
        exam_instance.message = str(e)
        exam_instance.save()
        print(f"Error: {e}")