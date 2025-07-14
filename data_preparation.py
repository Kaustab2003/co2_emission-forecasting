import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Optional: Use logging instead of print for production-ready code
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')


# -------------------- Data Loading --------------------

def load_data(filepath: str) -> pd.DataFrame:
    """Load CSV data and print an overview."""
    data = pd.read_csv(filepath)
    logging.info(f"✅ Data loaded successfully: {data.shape}")
    logging.info(f"\n🔍 Columns and types:\n{data.dtypes}")
    logging.info(f"\n🔍 First 5 rows:\n{data.head()}")
    logging.info(f"\n🔍 Summary statistics:\n{data.describe().T}")
    return data


# -------------------- Visualization --------------------

def plot_trends_over_time(df: pd.DataFrame, col: str, title: str, ylabel: str):
    """Generic function to plot a column's mean over time."""
    plt.figure(figsize=(10, 6))
    yearly_avg = df.groupby('year')[col].mean().reset_index()
    sns.lineplot(data=yearly_avg, x='year', y=col, marker='o')
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, title: str, xlabel: str, ylabel: str):
    """Generic scatter plot function."""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x_col, y=y_col, marker='^', color='coral')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_correlation_heatmap(df: pd.DataFrame, feature_cols: list):
    """Plot correlation heatmap for selected features."""
    plt.figure(figsize=(20, 15))
    sns.heatmap(df[feature_cols].corr(), annot=True, fmt=".2f", cmap='coolwarm', center=0)
    plt.title('📊 Feature Correlation Heatmap', fontsize=18)
    plt.tight_layout()
    plt.show()


def plot_country_time_series(df: pd.DataFrame, countries: list, y_col: str, title: str, ylabel: str):
    """Line plot of a metric over time for multiple countries."""
    df_filtered = df[df['country'].isin(countries)]
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_filtered, x='year', y=y_col, hue='country', marker='o')
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.legend(title='Country')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_pairwise_features(df: pd.DataFrame, countries: list, features: list):
    """Pairplot of selected features for selected countries."""
    df_filtered = df[df['country'].isin(countries)]
    sns.pairplot(df_filtered[features + ['country']], hue='country', height=2.5)
    plt.show()


def plot_4d_scatter(df: pd.DataFrame):
    """4D scatter plot using seaborn's relplot."""
    df = df[df['country'] != 'ARE']  # remove outlier if needed
    sns.set_theme(style="whitegrid", font_scale=1.3)
    g = sns.relplot(
        data=df,
        x='urb_pop_growth_perc',
        y='co2_per_cap',
        hue='en_per_cap',
        size='pop_urb_aggl_perc',
        palette='viridis',
        sizes=(20, 200),
        height=8,
        aspect=1.3
    )
    g.set_axis_labels('Urban population growth [%]', 'CO₂ emissions per capita [t]')
    g.fig.suptitle('4D Relationship: Urban Growth, CO₂, Energy Use & Urbanization')
    plt.tight_layout()
    plt.show()


# -------------------- VIF Calculation --------------------

def calculate_vif(df: pd.DataFrame, feature_cols: list):
    """Calculate VIF for the selected features."""
    X = df[feature_cols].dropna()
    vif_data = pd.DataFrame({'Feature': feature_cols})
    vif_data['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    logging.info(f"\n🔎 Variance Inflation Factors:\n{vif_data}\n")
    return vif_data


# -------------------- Main Function --------------------

def main():
    # File path
    file_path = 'data_cleaned.csv'

    # Load data
    df = load_data(file_path)

    # Add derived column
    df['en_ttl'] = df['en_per_gdp'] * df['gdp'] / 1000

    # Plot CO₂ emissions trends
    plot_trends_over_time(df, 'co2_per_cap', '🌍 Global Average CO₂ Emissions per Capita Over Time', 'CO₂ per Capita (metric tons)')

    # Scatter plot: Population vs CO₂ total emissions
    plot_scatter(df, 'pop', 'co2_ttl', 'Total CO₂ Emissions vs Population', 'Population', 'Total CO₂ emissions (KtCO₂)')

    # Correlation heatmap
    correlation_features = ['cereal_yield', 'fdi_perc_gdp', 'gni_per_cap', 'en_per_gdp', 'en_per_cap', 'en_ttl',
                            'co2_ttl', 'co2_per_cap', 'co2_per_gdp', 'pop_urb_aggl_perc', 'prot_area_perc',
                            'gdp', 'pop_growth_perc', 'pop', 'urb_pop_growth_perc']
    plot_correlation_heatmap(df, correlation_features)

    # Country comparison: CO₂ emissions per capita over time
    countries_to_compare = ['IND', 'USA', 'PAK', 'RUS', 'NZL']
    plot_country_time_series(df, countries_to_compare, 'co2_per_cap', 'CO₂ Emissions per Capita Over Time - Selected Countries', 'CO₂ per Capita (metric tons)')

    # Pairplot for selected countries
    pairplot_countries = ['IND', 'USA', 'PAK', 'RUS', 'NZL', 'MEX', 'MOZ', 'MYS', 'ETH', 'BEL']
    pairplot_features = ['cereal_yield', 'gni_per_cap', 'en_per_cap', 'co2_per_cap']
    plot_pairwise_features(df, pairplot_countries, pairplot_features)

    # 4D Scatter Plot
    plot_4d_scatter(df)

    # Calculate VIF
    vif_features = ['cereal_yield', 'fdi_perc_gdp', 'gni_per_cap', 'en_per_cap', 'co2_per_cap',
                    'pop_urb_aggl_perc', 'prot_area_perc', 'gdp', 'pop_growth_perc', 'urb_pop_growth_perc']
    calculate_vif(df, vif_features)


# -------------------- Script Entry Point --------------------

if __name__ == '__main__':
    main()
