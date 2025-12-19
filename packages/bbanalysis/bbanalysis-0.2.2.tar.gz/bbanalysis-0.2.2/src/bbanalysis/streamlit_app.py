import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load your data
# df_filtered = pd.read_csv('MLB_2018_2025_Full.csv')  # or however you load it

from bbanalysis.analysis import (
    filter_players_with_multiple_seasons,
    create_contract_indicators,
    run_mixed_effects_models,        # optional, if you want models
    generate_visualizations,         # optional, if you want plots
)

# Cache the processed data so it only runs once (or when the CSV changes)
@st.cache_data
def get_processed_df():
    # Step 1: Load the pre-merged file (fast!)
    print("Loading pre-merged data...")
    df_full = pd.read_csv('MLB_2018_2025_Full.csv')
    
    # Step 2: Filter players with enough seasons
    df_filtered = filter_players_with_multiple_seasons(df_full, min_seasons=5)
    
    # Step 3: Create the crucial contract indicators
    df_processed = create_contract_indicators(df_filtered)
    
    return df_processed

# Load the processed DataFrame with big contract year
df_filtered = get_processed_df()

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Baseball Contract Analysis",
    page_icon="⚾",
    layout="wide"
)

# ============================================
# TITLE AND INTRO
# ============================================
st.title("Baseball Contract Performance Analysis")
st.markdown("""
Explore how player performance changes after signing big contracts.
Analyze individual players, compare groups, and investigate the relationship between salary and performance.
            **By Isaac Miller and Jenna Worthen**
""")

# ============================================
# LOAD DATA
# ============================================

st.sidebar.header("Filters")

# ============================================
# SIDEBAR FILTERS
# ============================================

# Player selection
if 'player' in df_filtered.columns:
    all_players = sorted(df_filtered['player'].unique())
    selected_player = st.sidebar.selectbox(
        "Select Player for Individual Analysis",
        options=["Overview"] + all_players
    )
else:
    selected_player = "Overview"
    st.error("Player column not found in dataset")

# Age filter
if 'age' in df_filtered.columns:
    age_range = st.sidebar.slider(
        "Age Range",
        min_value=int(df_filtered['age'].min()),
        max_value=int(df_filtered['age'].max()),
        value=(int(df_filtered['age'].min()), int(df_filtered['age'].max()))
    )
else:
    age_range = None

# Year filter
year_range = st.sidebar.slider(
    "Year Range",
    min_value=int(df_filtered['year'].min()),
    max_value=int(df_filtered['year'].max()),
    value=(int(df_filtered['year'].min()), int(df_filtered['year'].max()))
)

# Contract size filter
salary_range = st.sidebar.slider(
    "Salary Range (Millions)",
    min_value=0.0,
    max_value=float(df_filtered['salary'].max() / 1_000_000),
    value=(0.0, float(df_filtered['salary'].max() / 1_000_000))
)

# Apply filters
df_display = df_filtered[
    (df_filtered['year'] >= year_range[0]) & 
    (df_filtered['year'] <= year_range[1]) &
    (df_filtered['salary'] >= salary_range[0] * 1_000_000) &
    (df_filtered['salary'] <= salary_range[1] * 1_000_000)
]

if age_range is not None:
    df_display = df_display[
        (df_display['age'] >= age_range[0]) & 
        (df_display['age'] <= age_range[1])
    ]

# ============================================
# MAIN CONTENT
# ============================================

if selected_player == "Overview":
    # ============================================
    # OVERVIEW TAB
    # ============================================
    
    st.header("Overall Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", df_display['player'].nunique())
    
    with col2:
        st.metric("Total Seasons", len(df_display))
    
    with col3:
        contracts = df_display[df_display['big_contract_year'] == True]
        st.metric("Big Contracts", len(contracts))
    
    with col4:
        avg_salary = df_display['salary'].mean() / 1_000_000
        st.metric("Avg Salary", f"${avg_salary:.1f}M")
    
    st.markdown("---")
    
    # Pre/Post contract comparison
    st.subheader("Pre vs Post Contract Performance")
    
    df_contract_analysis = df_display[
        (df_display['years_from_contract'].notna()) & 
        (df_display['years_from_contract'] >= -3) & 
        (df_display['years_from_contract'] <= 3)
    ]
    
    if len(df_contract_analysis) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pre/Post stats
            pre_data = df_contract_analysis[df_contract_analysis['post_contract'] == 0]
            post_data = df_contract_analysis[df_contract_analysis['post_contract'] == 1]
            
            comparison_df = pd.DataFrame({
                'Metric': ['OPS', 'WAR', 'Salary ($M)'],
                'Pre-Contract': [
                    pre_data['ops'].mean(),
                    pre_data['war'].mean(),
                    pre_data['salary'].mean() / 1_000_000
                ],
                'Post-Contract': [
                    post_data['ops'].mean(),
                    post_data['war'].mean(),
                    post_data['salary'].mean() / 1_000_000
                ]
            })
            comparison_df['Change'] = comparison_df['Post-Contract'] - comparison_df['Pre-Contract']
            
            st.dataframe(comparison_df.style.format({
                'Pre-Contract': '{:.3f}',
                'Post-Contract': '{:.3f}',
                'Change': '{:+.3f}'
            }), use_container_width=True)
        
        with col2:
            # Trajectory plot
            trajectory = df_contract_analysis.groupby('years_from_contract').agg({
                'ops': 'mean',
                'war': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trajectory['years_from_contract'],
                y=trajectory['ops'],
                mode='lines+markers',
                name='OPS',
                line=dict(width=3),
                marker=dict(size=10)
            ))
            
            fig.add_vline(x=0, line_dash="dash", line_color="red", 
                         annotation_text="Contract Year")
            
            fig.update_layout(
                title="Average OPS Around Contract Signing",
                xaxis_title="Years from Contract",
                yaxis_title="OPS",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Distribution plots
    st.subheader("Performance Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # OPS distribution
        fig = px.histogram(
            df_display,
            x='ops',
            nbins=50,
            title="OPS Distribution",
            labels={'ops': 'OPS', 'count': 'Frequency'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # WAR distribution
        fig = px.histogram(
            df_display,
            x='war',
            nbins=50,
            title="WAR Distribution",
            labels={'war': 'WAR', 'count': 'Frequency'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Salary vs Performance scatter
    st.subheader("Salary vs Performance")
    
    tab1, tab2 = st.tabs(["OPS vs Salary", "WAR vs Salary"])
    
    with tab1:
        fig = px.scatter(
            df_display,
            x='salary',
            y='ops',
            color='post_contract',
            hover_data=['player', 'year', 'age'],
            title="OPS vs Salary",
            labels={
                'salary': 'Salary ($)',
                'ops': 'OPS',
                'post_contract': 'Post-Contract'
            },
            color_discrete_map={0: 'blue', 1: 'red'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.scatter(
            df_display,
            x='salary',
            y='war',
            color='post_contract',
            hover_data=['player', 'year', 'age'],
            title="WAR vs Salary",
            labels={
                'salary': 'Salary ($)',
                'war': 'WAR',
                'post_contract': 'Post-Contract'
            },
            color_discrete_map={0: 'blue', 1: 'red'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

else:
    # ============================================
    # INDIVIDUAL PLAYER TAB
    # ============================================
    
    st.header(f"{selected_player}")
    
    player_data = df_filtered[df_filtered['player'] == selected_player].sort_values('year')
    
    if len(player_data) == 0:
        st.warning("No data available for this player")
    else:
        # Player stats summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Seasons", len(player_data))
        
        with col2:
            st.metric("Avg OPS", f"{player_data['ops'].mean():.3f}")
        
        with col3:
            st.metric("Avg WAR", f"{player_data['war'].mean():.2f}")
        
        with col4:
            st.metric("Peak Salary", f"${player_data['salary'].max()/1_000_000:.1f}M")
        
        st.markdown("---")
        
        # Career trajectory
        st.subheader("Career Trajectory")
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=("OPS Over Time", "WAR Over Time", "Salary Over Time"),
            vertical_spacing=0.1,
            row_heights=[0.33, 0.33, 0.34]
        )
        
        # OPS
        fig.add_trace(
            go.Scatter(
                x=player_data['year'],
                y=player_data['ops'],
                mode='lines+markers',
                name='OPS',
                line=dict(color='steelblue', width=3),
                marker=dict(size=10)
            ),
            row=1, col=1
        )
        
        # WAR
        fig.add_trace(
            go.Scatter(
                x=player_data['year'],
                y=player_data['war'],
                mode='lines+markers',
                name='WAR',
                line=dict(color='green', width=3),
                marker=dict(size=10)
            ),
            row=2, col=1
        )
        
        # Salary
        fig.add_trace(
            go.Scatter(
                x=player_data['year'],
                y=player_data['salary'] / 1_000_000,
                mode='lines+markers',
                name='Salary',
                line=dict(color='gold', width=3),
                marker=dict(size=10),
                fill='tozeroy'
            ),
            row=3, col=1
        )
        
        # Mark contract years
        contract_years = player_data[player_data['big_contract_year'] == True]
        for _, row in contract_years.iterrows():
            for i in range(1, 4):
                fig.add_vline(
                    x=row['year'],
                    line_dash="dash",
                    line_color="red",
                    row=i, col=1
                )
        
        fig.update_xaxes(title_text="Year", row=3, col=1)
        fig.update_yaxes(title_text="OPS", row=1, col=1)
        fig.update_yaxes(title_text="WAR", row=2, col=1)
        fig.update_yaxes(title_text="Salary ($M)", row=3, col=1)
        
        fig.update_layout(height=900, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Data table
        st.subheader("Season-by-Season Data")
        
        display_cols = ['year', 'age', 'salary', 'ops', 'war', 'big_contract_year', 'years_from_contract']
        available_cols = [col for col in display_cols if col in player_data.columns]
        
        st.dataframe(
            player_data[available_cols].style.format({
                'salary': '${:,.0f}',
                'ops': '{:.3f}',
                'war': '{:.1f}',
                'years_from_contract': '{:.0f}'
            }),
            use_container_width=True
        )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("**Data Source:** Baseball Reference (2018-2025) | **Analysis:** MLB Player Contract Performance")