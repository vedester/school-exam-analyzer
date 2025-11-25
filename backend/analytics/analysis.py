import pandas as pd
import numpy as np
import os
from django.core.files.base import ContentFile
from django.conf import settings
from io import BytesIO

def process_exam_file(exam_instance):
    try:
        file_path = exam_instance.file.path
        
        # 1. Read the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # 2. Smart Column Detection (Same as before)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_keywords = ['id', 'adm', 'phone', 'contact', 'year', 'stream', 'class', 'age']
        subject_cols = [col for col in numeric_cols if not any(k in col.lower() for k in exclude_keywords)]
        
        if not subject_cols:
            raise ValueError("No subjects detected.")

        # 3. CALCULATIONS
        df[subject_cols] = df[subject_cols].fillna(0)
        df['Total'] = df[subject_cols].sum(axis=1)
        df['Average'] = df['Total'] / len(subject_cols)
        # Rank: Method='min' means if two people tie at 1, the next is 3.
        df['Rank'] = df['Total'].rank(ascending=False, method='min')
        
        # Sort by Rank (Number 1 at top)
        df = df.sort_values(by='Rank')

        # 4. SUBJECT ANALYSIS (The "Summary" Sheet)
        # Calculate mean for each subject
        subject_means = df[subject_cols].mean().reset_index()
        subject_means.columns = ['Subject', 'Mean Score']
        
        # Find best performed subject
        best_subject_row = subject_means.loc[subject_means['Mean Score'].idxmax()]
        
        # Create a small summary dataframe
        summary_data = {
            'Metric': ['Class Mean Total', 'Best Subject', 'Best Subject Mean'],
            'Value': [df['Total'].mean(), best_subject_row['Subject'], best_subject_row['Mean Score']]
        }
        summary_df = pd.DataFrame(summary_data)

        # 5. SAVE TO NEW EXCEL FILE
        # We use BytesIO to save it to memory first, then to Django
        output = BytesIO()
        
        # Use ExcelWriter to create multiple sheets
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Student Ranks', index=False)
            subject_means.to_excel(writer, sheet_name='Subject Performance', index=False)
            summary_df.to_excel(writer, sheet_name='Overview', index=False)

        # 6. Save the file to the database field 'processed_file'
        output.seek(0)
        filename = f"Results_{exam_instance.title}.xlsx"
        exam_instance.processed_file.save(filename, ContentFile(output.read()), save=False)

        # 7. Update Status
        exam_instance.status = 'COMPLETED'
        exam_instance.message = (
            f"Analysis Ready! \n"
            f"Best Subject: {best_subject_row['Subject']} ({best_subject_row['Mean Score']:.1f})"
        )
        exam_instance.save()
        print("Results generated and saved.")

    except Exception as e:
        exam_instance.status = 'FAILED'
        exam_instance.message = str(e)
        exam_instance.save()
        print(f"Error: {e}")