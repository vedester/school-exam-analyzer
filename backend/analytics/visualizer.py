import matplotlib.pyplot as plt
from io import BytesIO

# Required for server environments like Render/Heroku to prevent GUI errors
plt.switch_backend('Agg')

def subject_performance_chart(subject_means_df):
    """
    Expects a DataFrame with columns: ['Subject', 'Mean Score']
    Returns: BytesIO object containing the PNG image
    """
    # Sort for better visuals
    data = subject_means_df.sort_values('Mean Score')

    plt.figure(figsize=(10, 6))
    
    # Logic: Red bars for < 50, Green for >= 50
    colors = ['#ff9999' if x < 50 else '#99ff99' for x in data['Mean Score']]
    
    plt.barh(data['Subject'], data['Mean Score'], color=colors)

    plt.title('Average Score per Subject')
    plt.xlabel('Mean Score')
    plt.tight_layout()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close() # Clean up memory
    
    return img_buffer


def pass_rate_chart(df):
    """
    Expects the full dataframe to calculate Pass/Fail counts.
    Returns: BytesIO object containing the PNG image
    """
    # Calculate Pass/Fail based on Average column
    pass_count = len(df[df['Average'] >= 50])
    fail_count = len(df[df['Average'] < 50])

    plt.figure(figsize=(6, 6))
    plt.pie(
        [pass_count, fail_count],
        labels=['Pass', 'Fail'],
        autopct='%1.1f%%',
        colors=['#66b3ff', '#ffcc99']
    )
    plt.title('Pass Rate (Average >= 50)')

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close() # Clean up memory
    
    return img_buffer