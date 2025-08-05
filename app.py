import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your data (replace with your dataset path)
df = pd.read_csv('heart_failure_clinical_records_dataset.csv')
df['Gender'] = df['sex'].map({1: 'Male', 0: 'Female'})

# Age group bins and labels
age_bins = [0, 40, 50, 60, 70, 150]
age_labels = ['Below 40', '40-50', '51-60', '61-70', '71+']
df['AgeGroup'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)

def calculate_summary(df_filtered):
    total = len(df_filtered)
    survived = (df_filtered['DEATH_EVENT'] == 0).sum()
    death = total - survived
    survival_rate = round(survived / total * 100, 2) if total else 0
    avg_age_survival = round(df_filtered[df_filtered['DEATH_EVENT'] == 0]['age'].mean(), 2) if survived else 0
    return survival_rate, avg_age_survival, survived, death

def summary_stats(df_filtered):
    grouped = df_filtered.groupby('AgeGroup').agg(
        Survival_Count=('DEATH_EVENT', lambda x: (x == 0).sum()),
        Avg_Serum_Creatinine=('serum_creatinine', 'mean'),
        Avg_Ejection_Fraction=('ejection_fraction', 'mean'),
        Smoking=('smoking', 'sum'),
        High_Blood_Pressure=('high_blood_pressure', 'sum'),
        Anaemia=('anaemia', 'sum'),
        Diabetes=('diabetes', 'sum'),
        Total=('DEATH_EVENT', 'count')
    ).reset_index()
    grouped['Survival_Rate'] = grouped['Survival_Count'] / grouped['Total'] * 100
    return grouped

def plot_dashboard(df_filtered):
    summary = summary_stats(df_filtered)
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))

    # Survival Count & Avg Serum Creatinine
    ax1 = axs[0,0]
    ax1.bar(summary['AgeGroup'], summary['Survival_Count'], color='red', label='Survival Count')
    ax1.set_ylabel('Survival Count', color='red')
    ax1.set_title('Survival Count & Avg Serum Creatinine by Age Group')
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.legend(loc='upper left')

    ax1b = ax1.twinx()
    ax1b.plot(summary['AgeGroup'], summary['Avg_Serum_Creatinine'], color='orange', marker='o', label='Avg Serum Creatinine')
    ax1b.set_ylabel('Avg Serum Creatinine', color='orange')
    ax1b.tick_params(axis='y', labelcolor='orange')
    ax1b.legend(loc='upper right')

    # Survival Count & Avg Ejection Fraction
    ax2 = axs[0,1]
    ax2.bar(summary['AgeGroup'], summary['Survival_Count'], color='purple', label='Survival Count')
    ax2.set_ylabel('Survival Count', color='purple')
    ax2.set_title('Survival Count & Avg Ejection Fraction by Age Group')
    ax2.tick_params(axis='y', labelcolor='purple')
    ax2.legend(loc='upper left')

    ax2b = ax2.twinx()
    ax2b.plot(summary['AgeGroup'], summary['Avg_Ejection_Fraction'], color='green', marker='o', label='Avg Ejection Fraction')
    ax2b.set_ylabel('Avg Ejection Fraction (%)', color='green')
    ax2b.tick_params(axis='y', labelcolor='green')
    ax2b.legend(loc='upper right')

    # Survival Rate by Age Group (Line plot)
    ax3 = axs[1,0]
    ax3.plot(summary['AgeGroup'], summary['Survival_Rate'], marker='o', color='blue')
    ax3.set_title('Survival Rate by Age Group (%)')
    ax3.set_ylabel('Survival Rate (%)')
    ax3.set_ylim(0, 100)

    # Impact of Smoking, High Blood Pressure, Anaemia and Diabetes by Age Group (stacked bar)
    ax4 = axs[1,1]
    width = 0.6
    x = np.arange(len(summary['AgeGroup']))
    ax4.bar(x, summary['Smoking'], width, label='Smoking')
    ax4.bar(x, summary['High_Blood_Pressure'], width, bottom=summary['Smoking'], label='High Blood Pressure')
    ax4.bar(x, summary['Anaemia'], width, bottom=summary['Smoking'] + summary['High_Blood_Pressure'], label='Anaemia')
    ax4.bar(x, summary['Diabetes'], width, bottom=summary['Smoking'] + summary['High_Blood_Pressure'] + summary['Anaemia'], label='Diabetes')
    ax4.set_xticks(x)
    ax4.set_xticklabels(summary['AgeGroup'])
    ax4.set_title('Impact of Smoking, High Blood Pressure, Anaemia & Diabetes by Age Group')
    ax4.legend()

    plt.tight_layout()
    st.pyplot(fig)

def main():
    # Side-by-side header with video
    col1, col2 = st.columns([3,1])
    with col1:
        st.title("Heart Failure Clinical Dashboard ❤️")
    with col2:
        video_file = open("heart.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes, format="video/mp4", start_time=0)

    # Gender selector
    gender = st.radio("Select Gender:", ['Female', 'Male'])

    # Filter data based on gender
    df_filtered = df[df['Gender'] == gender]

    # Calculate summary stats
    survival_rate, avg_age_survival, survived, death = calculate_summary(df_filtered)

    # Show summary stats side by side
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Survival Rate", f"{survival_rate}%")
    col2.metric("Avg Age of Survival", f"{avg_age_survival}")
    col3.metric("Total Survival", f"{survived}")
    col4.metric("Total Death", f"{death}")

    # Show plots
    plot_dashboard(df_filtered)

if __name__ == "__main__":
    main()
