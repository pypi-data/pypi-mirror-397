import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# ==============================================================================
# MLB Big Contract Performance Analysis Package
# ==============================================================================
# This module contains functions to perform a comprehensive analysis of whether
# large MLB contracts cause performance decline. It processes player stats and
# salary data, identifies big contract years, and runs mixed-effects models
# with proper controls (player random effects, year, age).
#
# Main entry point: run_full_analysis()
# ==============================================================================


def load_and_merge_data(stats_path='MLB_2018_2025_Cleaned.csv',
                        salary_path='salaries.csv',
                        output_merged_path='MLB_2018_2025_Full.csv'):
    """
    Load player stats and salary data, merge them, and save the merged dataset.
    
    Parameters:
        stats_path (str): Path to the cleaned player stats CSV.
        salary_path (str): Path to the salaries CSV.
        output_merged_path (str): Where to save the merged DataFrame.
    
    Returns:
        pd.DataFrame: Merged dataset with salary information.
    """
    print("Loading and merging data...")
    df = pd.read_csv(stats_path)
    salary = pd.read_csv(salary_path)
    
    # Standardize column names
    df.columns = df.columns.str.lower()
    
    # Merge on player name and year
    full = df.merge(salary, on=["player", "year"], how="left")
    
    # Save merged file for future use
    full.to_csv(output_merged_path, index=False)
    print(f"Merged data saved to {output_merged_path}")
    
    return full


def filter_players_with_multiple_seasons(df, min_seasons=5):
    """
    Filter to players with at least `min_seasons` seasons (default >4, i.e. 5+).
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with 'player' column.
        min_seasons (int): Minimum number of seasons required.
    
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    counts = df["player"].value_counts()
    qualified_players = counts[counts >= min_seasons].index
    df_filtered = df[df["player"].isin(qualified_players)].copy()
    print(f"Kept {len(qualified_players)} players with at least {min_seasons} seasons.")
    return df_filtered


def create_contract_indicators(df_filtered,
                               pct_threshold=0.5,
                               abs_threshold=5_000_000):
    """
    Create indicators for 'big contract' years and years relative to contract.
    
    Parameters:
        df_filtered (pd.DataFrame): DataFrame with salary and player info.
        pct_threshold (float): Percent salary increase to qualify as big contract.
        abs_threshold (float): Absolute dollar increase to qualify.
    
    Returns:
        pd.DataFrame: DataFrame with new columns:
                      - big_contract_year
                      - years_from_contract
                      - post_contract
    """
    print("Creating contract indicators...")
    df = df_filtered.sort_values(['player', 'year']).copy()
    
    # Year-over-year changes
    df['salary_change'] = df.groupby('player')['salary'].diff()
    df['pct_salary_change'] = df.groupby('player')['salary'].pct_change()
    
    # Flag big contract years
    df['big_contract_year'] = (
        (df['pct_salary_change'] > pct_threshold) |
        (df['salary_change'] > abs_threshold)
    )
    
    print(f"Found {df['big_contract_year'].sum()} big contract events.")
    
    # Mark years relative to first big contract for each player
    def mark_years_from_contract(player_df):
        if player_df['big_contract_year'].any():
            contract_year = player_df[player_df['big_contract_year']].iloc[0]['year']
            player_df['years_from_contract'] = player_df['year'] - contract_year
        else:
            player_df['years_from_contract'] = np.nan
        return player_df
    
    df = df.groupby('player', group_keys=False).apply(mark_years_from_contract)
    
    # Post-contract indicator (0 = pre, 1 = post, NaN = no contract)
    df['post_contract'] = (df['years_from_contract'] >= 0).astype(float)
    df.loc[df['years_from_contract'].isna(), 'post_contract'] = np.nan
    
    return df


def run_mixed_effects_models(df_processed, window_years=3):
    """
    Run the two main mixed-effects models:
        1. Overall salary → performance
        2. Pre/Post contract performance change (with controls)
    
    Parameters:
        df_processed (pd.DataFrame): DataFrame after contract indicators.
        window_years (int): How many years before/after contract to include.
    
    Returns:
        dict: Contains fitted models and restricted dataset for model2.
    """
    results = {}
    
    # Model 1: All players - Does salary predict performance?
    print("\nRunning Model 1: Salary → OPS (all players)")
    df_model1 = df_processed.dropna(subset=['ops', 'salary', 'war', 'year'])
    try:
        model1 = smf.mixedlm("ops ~ salary + war + year",
                            data=df_model1,
                            groups=df_model1["player"]).fit(reml=False)
        print(model1.summary())
        results['model1'] = model1
    except Exception as e:
        print(f"Model 1 failed: {e}")
    
    # Model 2: Pre/Post contract (restricted window)
    print("\nRunning Model 2: Pre vs Post contract performance")
    df_model2 = df_processed[
        (df_processed['years_from_contract'].notna()) &
        (df_processed['years_from_contract'].between(-window_years, window_years))
    ].copy()
    
    print(f"Using {len(df_model2)} observations from {df_model2['player'].nunique()} players.")
    
    # Formula: include age if available
    if 'age' in df_model2.columns:
        formula = "ops ~ post_contract + age + year"
    else:
        formula = "ops ~ post_contract + year"
        print("Note: 'age' column missing → excluded from model.")
    
    try:
        model2 = smf.mixedlm(formula,
                            data=df_model2,
                            groups=df_model2["player"]).fit(reml=False)
        print(model2.summary())
        
        # Interpretation
        coef = model2.params['post_contract']
        pval = model2.pvalues['post_contract']
        ci = model2.conf_int().loc['post_contract']
        
        print("\nPost-contract effect interpretation:")
        print(f"Coefficient: {coef:.4f} | p-value: {pval:.4f} | 95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")
        if pval < 0.05:
            print("Significant change detected." if coef < 0 else "Significant improvement detected.")
        else:
            print("No significant post-contract effect.")
        
        results['model2'] = model2
        results['df_model2'] = df_model2
    except Exception as e:
        print(f"Model 2 failed: {e}")
    
    return results


def generate_visualizations(df_model2, output_dir='plots'):
    """
    Generate all key visualizations and save them to disk.
    
    Parameters:
        df_model2 (pd.DataFrame): Restricted dataset around contract years.
        output_dir (str): Directory to save plots.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nGenerating visualizations → saved to '{output_dir}/'")
    
    # 1. Trajectory around contract signing
    trajectory = df_model2.groupby('years_from_contract').agg({
        'ops': ['mean', 'sem'],
        'war': ['mean', 'sem']
    }).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    x = trajectory['years_from_contract']
    
    # OPS
    ax1.errorbar(x, trajectory[('ops', 'mean')], yerr=trajectory[('ops', 'sem')],
                 marker='o', linewidth=2, capsize=5)
    ax1.axvline(0, color='red', linestyle='--', label='Contract Year')
    ax1.set_xlabel('Years from Contract Signing')
    ax1.set_ylabel('Average OPS')
    ax1.set_title('OPS Around Contract Signing')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # WAR
    ax2.errorbar(x, trajectory[('war', 'mean')], yerr=trajectory[('war', 'sem')],
                 marker='s', linewidth=2, capsize=5, color='green')
    ax2.axvline(0, color='red', linestyle='--')
    ax2.set_xlabel('Years from Contract Signing')
    ax2.set_ylabel('Average WAR')
    ax2.set_title('WAR Around Contract Signing')
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'contract_trajectory.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Box plots pre vs post
    df_model2['period'] = df_model2['post_contract'].map({0: 'Pre-Contract', 1: 'Post-Contract'})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    sns.boxplot(data=df_model2, x='period', y='ops', ax=ax1)
    ax1.set_title('OPS: Pre vs Post Contract')
    sns.boxplot(data=df_model2, x='period', y='war', ax=ax2)
    ax2.set_title('WAR: Pre vs Post Contract')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'contract_boxplots.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("All visualizations saved.")


def run_full_analysis(stats_path='MLB_2018_2025_Cleaned.csv',
                      salary_path='salaries.csv',
                      min_seasons=5,
                      output_dir='plots'):
    """
    Complete end-to-end analysis pipeline.
    Call this function from other scripts to reproduce the full analysis.
    """
    print("="*80)
    print("STARTING MLB BIG CONTRACT PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Step 1: Load and merge
    full_df = load_and_merge_data(stats_path, salary_path)
    
    # Step 2: Filter players
    df_filtered = filter_players_with_multiple_seasons(full_df, min_seasons=min_seasons)
    
    # Step 3: Create contract indicators
    df_processed = create_contract_indicators(df_filtered)
    
    # Step 4: Run models
    results = run_mixed_effects_models(df_processed)
    
    # Step 5: Visualizations (if model2 succeeded)
    if 'df_model2' in results:
        generate_visualizations(results['df_model2'], output_dir=output_dir)
    
    print("\nANALYSIS COMPLETE!")
    print("="*80)
    
    return {
        'full_data': full_df,
        'processed_data': df_processed,
        'models': results
    }


# ==============================================================================
# Example usage when run directly
# ==============================================================================
if __name__ == "__main__":
    run_full_analysis()