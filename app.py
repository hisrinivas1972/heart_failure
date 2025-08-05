import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/hisrinivas1972/heart_failure/main/heart_failure_clinical_records_dataset.csv"
    df = pd.read_csv(url)
    df['Gender'] = df['sex'].map({1: 'Male', 0: 'Female'})
    age_bins = [0, 40, 50, 60, 70, 150]
    age_labels = ['Below 40', '40-50', '51-60', '61-70', '71+']
    df['AgeGroup'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)
    return df

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
    survival_rate, avg_age_survival, survived, death = calculate_summary(df_filtered)
    
    # KPIs side by side with st.metric
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Survival Rate", f"{survival_rate}%")
    col2.metric("Average Age of Survival", f"{avg_age_survival}")
    col3.metric("Total Survival", f"{survived}")
    col4.metric("Total Death", f"{death}")
    
    summary = summary_stats(df_filtered)
    
    col5, col6 = st.columns(2)
    
    with col5:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=summary['AgeGroup'], y=summary['Survival_Count'], name='Survival Count', marker_color='red'))
        fig1.add_trace(go.Scatter(x=summary['AgeGroup'], y=summary['Avg_Serum_Creatinine'], mode='lines+markers', name='Avg Serum Creatinine', yaxis='y2', line=dict(color='orange')))
        fig1.update_layout(
            title="Survival Count & Avg Serum Creatinine by Age Group",
            yaxis=dict(title='Survival Count', color='red'),
            yaxis2=dict(title='Avg Serum Creatinine', overlaying='y', side='right', color='orange'),
            legend=dict(x=0, y=1.1, orientation='h')
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col6:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=summary['AgeGroup'], y=summary['Survival_Count'], name='Survival Count', marker_color='purple'))
        fig2.add_trace(go.Scatter(x=summary['AgeGroup'], y=summary['Avg_Ejection_Fraction'], mode='lines+markers', name='Avg Ejection Fraction', yaxis='y2', line=dict(color='green')))
        fig2.update_layout(
            title="Survival Count & Avg Ejection Fraction by Age Group",
            yaxis=dict(title='Survival Count', color='purple'),
            yaxis2=dict(title='Avg Ejection Fraction (%)', overlaying='y', side='right', color='green'),
            legend=dict(x=0, y=1.1, orientation='h')
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    col7, col8 = st.columns(2)
    
    with col7:
        fig3 = px.line(summary, x='AgeGroup', y='Survival_Rate', markers=True, title='Survival Rate by Age Group (%)')
        fig3.update_yaxes(range=[0, 100])
        st.plotly_chart(fig3, use_container_width=True)
    
    with col8:
        fig4 = go.Figure()
        x = summary['AgeGroup']
        fig4.add_trace(go.Bar(x=x, y=summary['Smoking'], name='Smoking'))
        fig4.add_trace(go.Bar(x=x, y=summary['High_Blood_Pressure'], name='High Blood Pressure', base=summary['Smoking']))
        base2 = summary['Smoking'] + summary['High_Blood_Pressure']
        fig4.add_trace(go.Bar(x=x, y=summary['Anaemia'], name='Anaemia', base=base2))
        base3 = base2 + summary['Anaemia']
        fig4.add_trace(go.Bar(x=x, y=summary['Diabetes'], name='Diabetes', base=base3))
        fig4.update_layout(barmode='stack', title='Impact of Smoking, High Blood Pressure, Anaemia & Diabetes by Age Group')
        st.plotly_chart(fig4, use_container_width=True)

def main():
    st.title("Heart Failure Clinical Dashboard")
    df = load_data()
    gender = st.radio("Select Gender:", options=['Female', 'Male'])
    df_filtered = df[df['Gender'] == gender]
    plot_dashboard(df_filtered)

if __name__ == "__main__":
    main()
