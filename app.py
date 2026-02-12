import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import sys
import base64
from io import BytesIO
from scipy import stats

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collect_tweets import get_sample_data, TwitterDataCollector
from src.calculate_stats import TweetStatisticsCalculator

st.set_page_config(
    page_title="Tweet Analyzer",
    layout="centered",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .stApp > header {display: none;}
    
    /* Remove all default Streamlit padding */
    .stApp {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stApp > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    div[class*="stAppViewBlockContainer"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide sidebar completely */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Main content container - perfectly centered */
    .main {
        max-width: 900px !important;
        margin: 0 auto !important;
        padding: 2rem 1.5rem !important;
    }
    
    .block-container {
        max-width: 900px !important;
        padding: 2rem 1.5rem !important;
        margin: 0 auto !important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global reset */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main container */
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #000000;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #666666;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    /* Input styling - clean and minimal */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border: 1px solid #e5e5e5 !important;
        border-radius: 8px !important;
        background: #ffffff !important;
        color: #000000 !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.15s ease !important;
    }
    
    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover,
    .stSelectbox > div > div:hover,
    .stNumberInput > div > div > input:hover {
        border-color: #000000 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #000000 !important;
        box-shadow: 0 0 0 1px #000000 !important;
        outline: none !important;
    }
    
    /* Button styling - black and white */
    .stButton > button {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        border: 1px solid #000000 !important;
    }
    
    .stButton > button:hover {
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }
    
    /* Secondary button style */
    .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #e5e5e5 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f5f5f5 !important;
        border-color: #000000 !important;
    }
    
    /* Metrics grid */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: #fafafa;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        padding: 1.25rem 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #000000;
        transform: translateY(-1px);
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #666666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #000000;
        line-height: 1;
    }
    
    .metric-unit {
        font-size: 0.85rem;
        color: #999999;
        margin-left: 2px;
    }
    
    /* Tab styling - centered, clean */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        justify-content: center;
        border-bottom: 1px solid #e5e5e5;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #666666 !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        transition: all 0.15s ease !important;
        font-size: 0.95rem !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #000000 !important;
        background: #f5f5f5 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
        border-bottom: 2px solid #000000 !important;
        background: transparent !important;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        background: #f0f0f0;
        color: #000000;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        border: 1px solid #e5e5e5;
        margin: 0.5rem 0;
    }
    
    .status-badge-success {
        background: #f0f0f0;
        border-left: 3px solid #22c55e;
    }
    
    .status-badge-warning {
        background: #fef9e7;
        border-left: 3px solid #f59e0b;
    }
    
    /* Insight box */
    .insight-box {
        background: #fafafa;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
        border-left: 3px solid #000000;
    }
    
    .insight-title {
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #000000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Info message */
    .info-message {
        background: #fafafa;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        color: #000000;
        font-size: 0.9rem;
        margin: 1rem 0;
        border-left: 3px solid #000000;
    }
    
    /* Section headers */
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #000000;
        margin: 1.75rem 0 1rem 0;
        letter-spacing: -0.01em;
    }
    
    .subsection-title {
        font-size: 1rem;
        font-weight: 600;
        color: #333333;
        margin: 1.25rem 0 0.75rem 0;
    }
    
    /* Divider */
    .divider {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: #e5e5e5;
    }
    
    /* Data table styling */
    .dataframe-container {
        background: white;
        border-radius: 10px;
        border: 1px solid #e5e5e5;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .stDataFrame {
        border: none !important;
    }
    
    .stDataFrame [data-testid="StyledDataFrameDataCell"] {
        font-size: 0.9rem !important;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: #e5e5e5 !important;
    }
    
    .stSlider [role="slider"] {
        background: #000000 !important;
        border: 2px solid white !important;
        width: 16px !important;
        height: 16px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 1rem !important;
    }
    
    .stRadio [role="radio"] {
        background: #ffffff !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 20px !important;
        padding: 0.5rem 1rem !important;
        cursor: pointer !important;
    }
    
    .stRadio [role="radio"][aria-checked="true"] {
        background: #000000 !important;
        border-color: #000000 !important;
        color: white !important;
    }
    
    .stRadio [role="radio"] > div:first-child {
        display: none !important;
    }
    
    /* Checkbox */
    .stCheckbox {
        margin: 0.5rem 0 !important;
    }
    
    .stCheckbox > div > div > div {
        border-color: #e5e5e5 !important;
    }
    
    .stCheckbox [aria-checked="true"] > div > div > div {
        background-color: #000000 !important;
        border-color: #000000 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 500 !important;
        color: #000000 !important;
        background: #fafafa !important;
        border-radius: 8px !important;
        border: 1px solid #e5e5e5 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #e5e5e5 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1.5rem !important;
    }
    
    /* Plotly charts - remove extra backgrounds */
    .js-plotly-plot {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #999999;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e5e5e5;
    }
    
    /* Hide default streamlit labels */
    label[data-testid="stWidgetLabel"] {
        display: none;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .metrics-row {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1rem !important;
            font-size: 0.85rem !important;
        }
    }
    
    
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_sample_data():
    return get_sample_data()

@st.cache_data(ttl=3600)
def load_uploaded_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def format_number(num):
    if pd.isna(num) or num is None:
        return "—"
    return f"{int(num):,}"

def format_float(num, decimals=2):
    if pd.isna(num) or num is None:
        return "—"
    return f"{num:.{decimals}f}"

def create_download_link(df, filename="tweet_data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="text-decoration: none; color: #000000; font-weight: 500;">📥 Download CSV</a>'
    return href

def render_metric_card(label, value, unit=""):
    """Render a consistent metric card"""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}<span class="metric-unit">{unit}</span></div>
    </div>
    """


def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">Tweet Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Summary statistics for celebrity tweets · Mean · Median · Distribution · Trends</p>', 
                unsafe_allow_html=True)
    
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        data_source = st.radio(
            "Data Source",
            ["Sample Data", "Upload CSV", "Live Collection"],
            index=0,
            label_visibility="collapsed",
            horizontal=True
        )
    
    with col2:
        if data_source == "Live Collection":
            st.markdown('<span class="status-badge status-badge-warning">Experimental</span>', 
                       unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    df = None
    username_filter = ""
    
    if data_source == "Sample Data":
        with st.spinner("Loading sample data..."):
            df = load_sample_data()
            st.markdown(f'<span class="status-badge status-badge-success">Loaded {len(df):,} tweets from 4 celebrities (2018-2024)</span>', 
                       unsafe_allow_html=True)
        
        with st.expander("Filter by username", expanded=False):
            all_users = [''] + sorted(df['username'].unique().tolist())
            username_filter = st.selectbox("Select user", all_users, format_func=lambda x: "All users" if x == "" else f"@{x}")
            if username_filter:
                df = df[df['username'] == username_filter]
                st.markdown(f'<span class="status-badge">Filtered: @{username_filter} ({len(df):,} tweets)</span>', 
                           unsafe_allow_html=True)
    
    elif data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed")
        
        if uploaded_file is not None:
            df = load_uploaded_data(uploaded_file)
            if df is not None:
                st.markdown(f'<span class="status-badge status-badge-success">Loaded {len(df):,} tweets</span>', 
                           unsafe_allow_html=True)
        else:
            st.info("Upload a CSV file with tweet data")
            st.stop()
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            username = st.text_input(
                "Twitter username", 
                value="elonmusk",
                key="live_username",
                label_visibility="collapsed",
                placeholder="username (without @)"
            )
        
        with col2:
            start_year = st.number_input(
                "From", 
                min_value=2010, 
                max_value=2024, 
                value=2022, 
                label_visibility="collapsed",
                key="start_year"
            )
        
        with col3:
            end_year = st.number_input(
                "To", 
                min_value=2010, 
                max_value=2024, 
                value=2023, 
                label_visibility="collapsed",
                key="end_year"
            )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            collect_button = st.button("Collect Tweets", use_container_width=True)
        
        if collect_button:
            with st.spinner(f"Collecting tweets from @{username}..."):
                collector = TwitterDataCollector()
                years = list(range(start_year, end_year + 1))
                df = collector.collect_celebrity_tweets(username, years)
                
                if not df.empty:
                    safe_user = username.replace('<', '&lt;').replace('>', '&gt;')
                    st.markdown(
                        f'<span class="status-badge status-badge-success">✓ Collected {len(df):,} tweets from @{safe_user}</span>',
                        unsafe_allow_html=True
                    )
                else:
                    st.error("No tweets collected. Using sample data instead.")
                    df = load_sample_data()
        else:
            st.info("Enter a username and click 'Collect Tweets'")
            st.stop()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.error("No data available")
        st.stop()
    
    calculator = TweetStatisticsCalculator(df)
    report = calculator.generate_full_report()
    overall_stats = report.get('overall_stats', {})
    
    st.markdown('<div class="metrics-row">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_metric_card("Total Tweets", format_number(report['dataset_info']['total_tweets'])), 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(render_metric_card("Mean", format_float(overall_stats.get('mean', 0), 1), "words"), 
                   unsafe_allow_html=True)
    with col3:
        st.markdown(render_metric_card("Median", format_float(overall_stats.get('median', 0), 1), "words"), 
                   unsafe_allow_html=True)
    with col4:
        st.markdown(render_metric_card("Std Dev", format_float(overall_stats.get('std', 0), 2), ""), 
                   unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    insight_html = f"""
    <div class="insight-box">
        <div class="insight-title">Summary Statistics</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 0.5rem;">
            <div>
                <span style="color: #666666; font-size: 0.8rem;">DISTRIBUTION</span><br>
                <span style="font-weight: 600;">{'Right-skewed' if overall_stats.get('mean', 0) > overall_stats.get('median', 0) else 'Left-skewed'}</span>
                <span style="color: #666666; font-size: 0.85rem; margin-left: 0.5rem;">(μ > M)</span>
            </div>
            <div>
                <span style="color: #666666; font-size: 0.8rem;">VARIABILITY</span><br>
                <span style="font-weight: 600;">{'High' if overall_stats.get('cv', 0) > 50 else 'Moderate'}</span>
                <span style="color: #666666; font-size: 0.85rem; margin-left: 0.5rem;">CV = {overall_stats.get('cv', 0):.1f}%</span>
            </div>
            <div>
                <span style="color: #666666; font-size: 0.8rem;">TYPICAL RANGE</span><br>
                <span style="font-weight: 600;">{overall_stats.get('q1', 0):.0f} – {overall_stats.get('q3', 0):.0f}</span>
                <span style="color: #666666; font-size: 0.85rem; margin-left: 0.5rem;">words (IQR)</span>
            </div>
            <div>
                <span style="color: #666666; font-size: 0.8rem;">SHAPE</span><br>
                <span style="font-weight: 600;">{report.get('distribution', {}).get('distribution_type', 'Skewed')}</span>
                <span style="color: #666666; font-size: 0.85rem; margin-left: 0.5rem;">γ₁ = {overall_stats.get('skewness', 0):.2f}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(insight_html, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Distribution", "Year-over-Year", "Compare Users", "Raw Data"]
    )
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="subsection-title">Five-Number Summary</div>', unsafe_allow_html=True)
            
            summary_data = {
                'Statistic': ['Minimum', 'Q1 (25%)', 'Median (Q2)', 'Q3 (75%)', 'Maximum'],
                'Words': [
                    f"{overall_stats.get('min', 0):.0f}",
                    f"{overall_stats.get('q1', 0):.0f}",
                    f"{overall_stats.get('median', 0):.0f}",
                    f"{overall_stats.get('q3', 0):.0f}",
                    f"{overall_stats.get('max', 0):.0f}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(summary_df, use_container_width=True, hide_index=True, 
                        column_config={
                            "Statistic": st.column_config.TextColumn("Statistic"),
                            "Words": st.column_config.TextColumn("Words")
                        })
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="subsection-title">Distribution Metrics</div>', unsafe_allow_html=True)
            
            dist_stats = report.get('distribution', {})
            percentiles = dist_stats.get('percentiles', {})
            
            metrics_data = {
                'Metric': ['Skewness', 'Kurtosis', 'Range', 'IQR', '95th Percentile'],
                'Value': [
                    f"{overall_stats.get('skewness', 0):.3f}",
                    f"{overall_stats.get('kurtosis', 0):.3f}",
                    f"{overall_stats.get('range', 0):.0f}",
                    f"{overall_stats.get('iqr', 0):.0f}",
                    f"{percentiles.get('p95', 0):.0f}"
                ]
            }
            
            metrics_df = pd.DataFrame(metrics_data)
            
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="subsection-title">Word Count Distribution</div>', unsafe_allow_html=True)
        
        fig = px.histogram(
            df,
            x='word_count',
            nbins=30,
            histnorm='probability density',
            labels={'word_count': 'Words per Tweet', 'density': 'Density'},
            color_discrete_sequence=['#222222']
        )
        
        kde_x = np.linspace(df['word_count'].min(), df['word_count'].max(), 200)
        kde_y = stats.gaussian_kde(df['word_count'])(kde_x)
        
        fig.add_trace(
            go.Scatter(
                x=kde_x,
                y=kde_y,
                mode='lines',
                name='KDE',
                line=dict(color='#666666', width=2)
            )
        )
        
        fig.add_vline(x=overall_stats.get('mean', 0), 
                     line_dash="dash", 
                     line_color="#666666",
                     annotation_text="Mean",
                     annotation_position="top")
        
        fig.add_vline(x=overall_stats.get('median', 0), 
                     line_dash="dot", 
                     line_color="#000000",
                     annotation_text="Median",
                     annotation_position="bottom")
        
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=40, r=40, t=20, b=40),
            bargap=0.08,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Inter', size=11),
            xaxis=dict(
                gridcolor='#f0f0f0',
                title_font=dict(size=12),
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                gridcolor='#f0f0f0',
                title_font=dict(size=12),
                tickfont=dict(size=11)
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Normality Check (Q-Q Plot)", expanded=False):
            fig_qq = plt.figure(figsize=(10, 4))
            ax = fig_qq.add_subplot(111)
            
            stats.probplot(df['word_count'], dist="norm", plot=ax)
            ax.set_title("Q-Q Plot", fontsize=13, fontweight='bold')
            ax.set_xlabel("Theoretical Quantiles", fontsize=11)
            ax.set_ylabel("Sample Quantiles", fontsize=11)
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig_qq)
            
            st.markdown(f"""
            <div class="info-message">
                <strong>Interpretation:</strong> Points deviate from the red line → data is 
                <strong>{'not ' if abs(dist_stats.get('skewness', 0)) > 0.5 else ''}normally distributed</strong>.
                Skewness = {overall_stats.get('skewness', 0):.3f}, Kurtosis = {overall_stats.get('kurtosis', 0):.3f}
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        yearly_df = calculator.yearly_summary_stats()
        
        if not yearly_df.empty and len(yearly_df) > 1:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(render_metric_card("Years", f"{yearly_df['year'].min()}–{yearly_df['year'].max()}"), 
                           unsafe_allow_html=True)
            with col2:
                change = yearly_df['mean'].iloc[-1] - yearly_df['mean'].iloc[0]
                direction = "↑" if change > 0 else "↓"
                st.markdown(render_metric_card("Mean Change", f"{direction} {abs(change):.1f}", "words"), 
                           unsafe_allow_html=True)
            with col3:
                pct_change = ((yearly_df['mean'].iloc[-1] - yearly_df['mean'].iloc[0]) / yearly_df['mean'].iloc[0]) * 100
                st.markdown(render_metric_card("Percent Change", f"{pct_change:+.1f}", "%"), 
                           unsafe_allow_html=True)
            with col4:
                vol_change = yearly_df['std'].iloc[-1] - yearly_df['std'].iloc[0]
                st.markdown(render_metric_card("Volatility Δ", f"{vol_change:+.1f}", ""), 
                           unsafe_allow_html=True)
            
            st.markdown('<div class="subsection-title">Trend Analysis</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=yearly_df['year'],
                y=yearly_df['mean'],
                name='Mean',
                line=dict(color='#000000', width=2.5),
                mode='lines+markers',
                marker=dict(size=8, color='#000000')
            ))
            
            fig.add_trace(go.Scatter(
                x=yearly_df['year'],
                y=yearly_df['median'],
                name='Median',
                line=dict(color='#666666', width=2, dash='dash'),
                mode='lines+markers',
                marker=dict(size=8, color='#666666')
            ))
            
            fig.add_trace(go.Scatter(
                x=yearly_df['year'].tolist() + yearly_df['year'].tolist()[::-1],
                y=(yearly_df['mean'] + yearly_df['std']).tolist() + (yearly_df['mean'] - yearly_df['std']).tolist()[::-1],
                fill='toself',
                fillcolor='rgba(0,0,0,0.05)',
                line=dict(width=0),
                showlegend=False,
                name='±1 Std Dev'
            ))
            
            fig.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=20, b=40),
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Inter', size=11),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis=dict(
                    title="Year",
                    gridcolor='#f0f0f0',
                    tickmode='array',
                    tickvals=yearly_df['year']
                ),
                yaxis=dict(
                    title="Word Count",
                    gridcolor='#f0f0f0'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="subsection-title">Distribution by Year</div>', unsafe_allow_html=True)
            
            fig_box = px.box(
                df,
                x='year',
                y='word_count',
                labels={'year': 'Year', 'word_count': 'Words per Tweet'},
                color_discrete_sequence=['#222222']
            )
            
            fig_box.update_layout(
                showlegend=False,
                height=450,
                margin=dict(l=40, r=40, t=20, b=40),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Inter', size=11),
                xaxis=dict(gridcolor='#f0f0f0'),
                yaxis=dict(gridcolor='#f0f0f0')
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
            
            with st.expander("View Yearly Statistics", expanded=False):
                display_df = yearly_df[['year', 'tweet_count', 'mean', 'median', 'std', 'min', 'max']].copy()
                display_df.columns = ['Year', 'Tweets', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']
                display_df = display_df.round(2)
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("Need at least 2 years of data for yearly analysis")
    
    with tab3:
        user_stats = calculator.user_comparison_stats()
        
        if not user_stats.empty and len(user_stats) > 1:
            st.markdown('<div class="subsection-title">Average Word Count by User</div>', unsafe_allow_html=True)
            
            fig_compare = px.bar(
                user_stats,
                x='username',
                y='mean_words',
                error_y='std_words',
                labels={'username': 'User', 'mean_words': 'Average Words'},
                color_discrete_sequence=['#222222']
            )
            
            fig_compare.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=20, b=40),
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Inter', size=11),
                xaxis=dict(gridcolor='#f0f0f0'),
                yaxis=dict(gridcolor='#f0f0f0', title="Average Words")
            )
            
            st.plotly_chart(fig_compare, use_container_width=True)
            
            st.markdown('<div class="subsection-title">User Statistics</div>', unsafe_allow_html=True)
            
            display_users = user_stats[['username', 'displayname', 'tweet_count', 'mean_words', 'median_words', 'std_words']].copy()
            display_users.columns = ['Username', 'Name', 'Tweets', 'Mean', 'Median', 'Std Dev']
            display_users = display_users.round(2)
            
            st.dataframe(display_users, use_container_width=True, hide_index=True)
            
            if 'industry' in user_stats.columns:
                st.markdown('<div class="subsection-title">Industry Comparison</div>', unsafe_allow_html=True)
                
                industry_stats = user_stats.groupby('industry').agg({
                    'mean_words': 'mean',
                    'tweet_count': 'sum',
                    'std_words': 'mean'
                }).reset_index()
                
                industry_stats.columns = ['Industry', 'Avg Words', 'Total Tweets', 'Avg Variability']
                industry_stats = industry_stats.round(2)
                
                st.dataframe(industry_stats, use_container_width=True, hide_index=True)
        else:
            if len(user_stats) == 1:
                st.info("Only one user in dataset. Add more users for comparison.")
            else:
                st.info("No user comparison data available.")
    
    with tab4:
        st.markdown('<div class="subsection-title">Tweet Data</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'year' in df.columns:
                years = ['All'] + sorted(df['year'].unique().tolist())
                selected_year = st.selectbox("Year", years, index=0)
        
        with col2:
            if 'username' in df.columns:
                users = ['All'] + sorted(df['username'].unique().tolist())
                selected_user = st.selectbox("User", users, index=0)
        
        with col3:
            word_count_slider = st.slider(
                "Word count",
                min_value=int(df['word_count'].min()),
                max_value=int(df['word_count'].max()),
                value=(int(df['word_count'].min()), int(df['word_count'].max()))
            )
        
        filtered_df = df.copy()
        
        if selected_year != 'All':
            filtered_df = filtered_df[filtered_df['year'] == selected_year]
        
        if selected_user != 'All':
            filtered_df = filtered_df[filtered_df['username'] == selected_user]
        
        filtered_df = filtered_df[
            (filtered_df['word_count'] >= word_count_slider[0]) & 
            (filtered_df['word_count'] <= word_count_slider[1])
        ]
        
        st.markdown(f'<span class="status-badge">Showing {len(filtered_df):,} of {len(df):,} tweets</span>', 
                   unsafe_allow_html=True)
        
        display_cols = ['date', 'username', 'content', 'word_count', 'like_count', 'retweet_count']
        display_cols = [col for col in display_cols if col in filtered_df.columns]
        
        if 'content' in filtered_df.columns:
            filtered_df['content_short'] = filtered_df['content'].str[:50] + '...'
            display_cols = ['date', 'username', 'content_short', 'word_count', 'like_count', 'retweet_count']
        
        st.dataframe(
            filtered_df[display_cols].sort_values('date', ascending=False).head(100),
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": st.column_config.DatetimeColumn("Date"),
                "username": st.column_config.TextColumn("User"),
                "content_short": st.column_config.TextColumn("Content"),
                "word_count": st.column_config.NumberColumn("Words"),
                "like_count": st.column_config.NumberColumn("Likes"),
                "retweet_count": st.column_config.NumberColumn("Retweets")
            }
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Download CSV", use_container_width=True, type="secondary"):
                csv_link = create_download_link(filtered_df, f"tweets_{datetime.now().strftime('%Y%m%d')}.csv")
                st.markdown(csv_link, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="footer">
        <span style="font-weight: 500;">Twitter Word Count Analyzer</span> · 
        Summary Statistics Project · 
        Mean · Median · Std Dev · IQR · Skewness · 
        Built with Streamlit
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()