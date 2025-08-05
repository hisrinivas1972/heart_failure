import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import base64

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

    col1, col2 = st.columns([4, 1])
    with col1:
        gender = st.radio("Select Gender:", options=['Female', 'Male'], horizontal=True)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Survival Rate", f"{survival_rate}%")
        kpi2.metric("Average Age of Survival", f"{avg_age_survival}")
        kpi3.metric("Total Survival", f"{survived}")
        kpi4.metric("Total Death", f"{death}")
    with col2:
        video_path = "heart.mp4"
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
        encoded = base64.b64encode(video_bytes).decode()
        video_html = f"""
        <video width="100%" autoplay loop muted playsinline>
            <source src="data:video/mp4;base64,{encoded}" type="video/mp4">
        </video>
        """
        st.components.v1.html(video_html, height=180)

    summary = summary_stats(df_filtered)
    cols = st.columns(4)

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=summary['AgeGroup'], y=summary['Survival_Count'], name='Survival Count', marker_color='red'))
    fig1.add_trace(go.Scatter(x=summary['AgeGroup'], y=summary['Avg_Serum_Creatinine'], mode='lines+markers', name='Avg Serum Creatinine', yaxis='y2', line=dict(color='orange')))
    fig1.update_layout(
        height=280, title="Survival Count & Avg Serum Creatinine",
        yaxis=dict(title='Survival Count', color='red'),
        yaxis2=dict(title='Avg Serum Creatinine', overlaying='y', side='right', color='orange'),
        legend=dict(x=0, y=1.1, orientation='h')
    )
    cols[0].plotly_chart(fig1, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=summary['AgeGroup'], y=summary['Survival_Count'], name='Survival Count', marker_color='purple'))
    fig2.add_trace(go.Scatter(x=summary['AgeGroup'], y=summary['Avg_Ejection_Fraction'], mode='lines+markers', name='Avg Ejection Fraction', yaxis='y2', line=dict(color='green')))
    fig2.update_layout(
        height=280, title="Survival Count & Avg Ejection Fraction",
        yaxis=dict(title='Survival Count', color='purple'),
        yaxis2=dict(title='Avg Ejection Fraction (%)', overlaying='y', side='right', color='green'),
        legend=dict(x=0, y=1.1, orientation='h')
    )
    cols[1].plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(summary, x='AgeGroup', y='Survival_Rate', markers=True, title='Survival Rate by Age Group (%)')
    fig3.update_layout(height=280)
    fig3.update_yaxes(range=[0, 100])
    cols[2].plotly_chart(fig3, use_container_width=True)

    fig4 = go.Figure()
    x = summary['AgeGroup']
    fig4.add_trace(go.Bar(x=x, y=summary['Smoking'], name='Smoking'))
    fig4.add_trace(go.Bar(x=x, y=summary['High_Blood_Pressure'], name='High Blood Pressure', base=summary['Smoking']))
    base2 = summary['Smoking'] + summary['High_Blood_Pressure']
    fig4.add_trace(go.Bar(x=x, y=summary['Anaemia'], name='Anaemia', base=base2))
    base3 = base2 + summary['Anaemia']
    fig4.add_trace(go.Bar(x=x, y=summary['Diabetes'], name='Diabetes', base=base3))
    fig4.update_layout(barmode='stack', height=280, title='Impact of Smoking, High Blood Pressure, Anaemia & Diabetes')
    cols[3].plotly_chart(fig4, use_container_width=True)

    return gender

def play_heartbeat_audio():
    with open("heartbeat.mp3", "rb") as f:
        audio_bytes = f.read()
    encoded_audio = base64.b64encode(audio_bytes).decode()

    # Hidden audio tag for autoplay
    audio_html = f"""
    <audio id="heartbeatAudio" loop autoplay muted style="display:none;">
        <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">
    </audio>

    <script>
    // Try to play muted audio for autoplay policy compliance
    const audio = document.getElementById('heartbeatAudio');
    audio.muted = true;
    audio.play();

    // Unmute after user interaction
    window.addEventListener('click', () => {{
        audio.muted = false;
        audio.play();
    }});
    </script>
    """
    st.components.v1.html(audio_html, height=0)

    # Button to unmute/play audio manually if needed
    if st.button("🔊 Play Heartbeat Sound"):
        st.experimental_javascript("""
            var audio = document.getElementById('heartbeatAudio');
            audio.muted = false;
            audio.play();
        """)

def main():
    st.markdown("<h1 style='margin-bottom: 0rem;'>❤️ Heart Failure Clinical Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_data()

    # Play heartbeat audio with muted autoplay + user click unmute
    play_heartbeat_audio()

    if "gender" not in st.session_state:
        st.session_state["gender"] = "Female"

    gender_selected = plot_dashboard(df[df['Gender'] == st.session_state["gender"]])
    st.session_state["gender"] = gender_selected

if __name__ == "__main__":
    main()
