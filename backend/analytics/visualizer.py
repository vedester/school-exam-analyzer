# backend/analytics/visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Non-GUI backend for server safety
plt.switch_backend('Agg')
sns.set_theme(style="whitegrid") # Makes charts look modern

def subject_performance_chart(subject_means_df):
    """
    Horizontal Bar Chart: Subject vs Mean Score
    """
    data = subject_means_df.sort_values('Mean Score', ascending=True)
    
    plt.figure(figsize=(10, 6))
    
    # Modern color palette
    colors = ['#e74c3c' if x < 50 else '#2ecc71' for x in data['Mean Score']]
    
    bars = plt.barh(data['Subject'], data['Mean Score'], color=colors, alpha=0.8)
    
    plt.title('Subject Performance Analysis', fontsize=14, pad=20)
    plt.xlabel('Mean Score', fontsize=12)
    plt.xlim(0, 100)
    
    # Add values to the end of bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, 
                 f'{width:.1f}', va='center', fontsize=10)

    plt.tight_layout()
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    plt.close()
    return img_buffer

def pass_rate_chart(df):
    """
    Donut Chart: Pass vs Fail
    """
    pass_count = len(df[df['Average'] >= 50])
    fail_count = len(df[df['Average'] < 50])
    
    plt.figure(figsize=(6, 6))
    
    # Donut chart style
    wedges, texts, autotexts = plt.pie(
        [pass_count, fail_count],
        labels=['Pass (>=50)', 'Fail (<50)'],
        autopct='%1.1f%%',
        startangle=90,
        colors=['#3498db', '#e67e22'],
        pctdistance=0.85,
        explode=(0.05, 0)
    )
    
    # Draw circle for donut effect
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.title('Class Pass Rate', fontsize=14)
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    plt.close()
    return img_buffer

def grade_distribution_chart(df):
    """
    New Chart: Shows count of A, B, C, etc.
    This is CRITICAL for Kenyan Exam Analysis.
    """
    # Order of grades
    grade_order = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E']
    
    # Count grades
    grade_counts = df['Overall Grade'].value_counts().reindex(grade_order, fill_value=0)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=grade_counts.index, y=grade_counts.values, palette="viridis")
    
    plt.title('Grade Distribution', fontsize=14)
    plt.ylabel('Number of Students')
    plt.xlabel('Grade')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    plt.close()
    return img_buffer