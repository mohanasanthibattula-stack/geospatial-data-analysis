"""
Geospatial Data Analysis & Interactive Mapping Pipeline
Author: Geospatial Data Analyst & MLOps Engineer
Dataset: india_regional_market_v2.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster, HeatMap

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "india_regional_market_v2.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
MAP_OUTPUT_PATH = os.path.join(BASE_DIR, "geospatial_market_analysis.html")

os.makedirs(CHARTS_DIR, exist_ok=True)

# 1. Load Data
df = pd.read_csv(DATA_PATH)
print(f"[INFO] Ingested dataset with {len(df)} records across {df['City'].nunique()} cities and {df['State'].nunique()} states.")

# 2. Feature Engineering & Key Metrics Computation
df['OpportunityScore'] = (df['MonthlySearchDemand'] * df['LeadConversionRate']) / (df['ExistingCompetitors'] + 1)
df['EstimatedRevenuePotential'] = df['MonthlySearchDemand'] * df['LeadConversionRate'] * df['MedianAnnualIncomeINR']
df['MarketSaturationRatio'] = df['ExistingCompetitors'] / (df['MonthlySearchDemand'] / 1000.0)
df['CAC_to_Income_Ratio'] = df['EstimatedAcquisitionCostINR'] / df['MedianAnnualIncomeINR']

# Identify Top 3 High-Potential Underserved Regions
top_3_regions = df.sort_values(by='OpportunityScore', ascending=False).head(3).copy()
print("\n=== TOP 3 HIGH-POTENTIAL UNDERSERVED REGIONS ===")
for rank, (_, row) in enumerate(top_3_regions.iterrows(), 1):
    print(f"Rank {rank}: {row['RegionID']} - {row['City']}, {row['State']}")
    print(f"   Monthly Search Demand : {row['MonthlySearchDemand']:,}")
    print(f"   Existing Competitors  : {row['ExistingCompetitors']}")
    print(f"   Lead Conversion Rate  : {row['LeadConversionRate']:.2%}")
    print(f"   Estimated CAC         : INR {row['EstimatedAcquisitionCostINR']}")
    print(f"   Median Annual Income  : INR {row['MedianAnnualIncomeINR']:,}")
    print(f"   Opportunity Score     : {row['OpportunityScore']:.2f}")
    print(f"   Est. Monthly Revenue  : INR {row['EstimatedRevenuePotential']:,.2f}")
    print("-" * 50)

# Set style for Matplotlib/Seaborn
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -------------------------------------------------------------
# CHART 1: Monthly Search Demand vs Existing Competitors
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
scatter = ax.scatter(
    df['ExistingCompetitors'],
    df['MonthlySearchDemand'],
    c=df['OpportunityScore'],
    cmap='viridis',
    s=df['EstimatedRevenuePotential'] / 1.5e6,
    alpha=0.75,
    edgecolors='w',
    linewidth=0.5
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Opportunity Score = (Demand × Conversion) / (Competitors + 1)', fontsize=11, fontweight='bold')

# Annotate Top 3
for _, row in top_3_regions.iterrows():
    ax.annotate(
        f"{row['RegionID']}: {row['City']}\nScore: {row['OpportunityScore']:.1f}",
        xy=(row['ExistingCompetitors'], row['MonthlySearchDemand']),
        xytext=(row['ExistingCompetitors'] + 0.6, row['MonthlySearchDemand'] - 40),
        arrowprops=dict(facecolor='#d90429', edgecolor='none', shrink=0.08, width=1.5, headwidth=6),
        fontsize=9.5,
        fontweight='bold',
        color='#b7094c',
        bbox=dict(boxstyle="round,pad=0.3", fc="#fdf0ed", ec="#d90429", lw=1)
    )

ax.set_title("Market Demand vs. Competitor Density Across Indian Regional Hubs", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Existing Regional Competitors (Count)", fontsize=12, fontweight='bold')
ax.set_ylabel("Monthly Search Demand (Searches/Month)", fontsize=12, fontweight='bold')
ax.set_xlim(-0.5, 16.5)
plt.tight_layout()
chart1_path = os.path.join(CHARTS_DIR, "01_demand_vs_competitors.png")
plt.savefig(chart1_path, dpi=300)
plt.close()
print(f"[SAVED] {chart1_path}")

# -------------------------------------------------------------
# CHART 2: Top 10 Underserved Regions Ranked by Opportunity Score
# -------------------------------------------------------------
top_10_df = df.sort_values(by='OpportunityScore', ascending=False).head(10).copy()
top_10_df['Label'] = top_10_df['RegionID'] + " (" + top_10_df['City'] + " - " + top_10_df['PopulationSegment'] + ")"

fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
colors = ['#10b981' if i < 3 else '#3b82f6' for i in range(len(top_10_df))]
bars = ax.barh(top_10_df['Label'][::-1], top_10_df['OpportunityScore'][::-1], color=colors[::-1], edgecolor='none', height=0.65)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}",
            va='center', ha='left', fontsize=9.5, fontweight='bold', color='#1f2937')

ax.set_title("Top 10 High-Potential Regional Expansion Targets (Opportunity Score)", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Opportunity Score = (Monthly Demand × Conversion) / (Competitors + 1)", fontsize=11, fontweight='bold')
ax.set_xlim(0, 140)
# Custom legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#10b981', label='Top 3 High-Potential Underserved Targets'),
    Patch(facecolor='#3b82f6', label='Secondary High-Value Candidates')
]
ax.legend(handles=legend_elements, loc='lower right', frameon=True, fontsize=10)
plt.tight_layout()
chart2_path = os.path.join(CHARTS_DIR, "02_top_underserved_regions.png")
plt.savefig(chart2_path, dpi=300)
plt.close()
print(f"[SAVED] {chart2_path}")

# -------------------------------------------------------------
# CHART 3: City-Level Aggregated Market Metrics
# -------------------------------------------------------------
city_summary = df.groupby('City').agg(
    TotalDemand=('MonthlySearchDemand', 'sum'),
    AvgCompetitors=('ExistingCompetitors', 'mean'),
    MeanOpportunityScore=('OpportunityScore', 'mean'),
    TotalRevenuePotential=('EstimatedRevenuePotential', 'sum')
).sort_values(by='MeanOpportunityScore', ascending=False).reset_index()

fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

x = np.arange(len(city_summary))
width = 0.38

rects1 = ax1.bar(x - width/2, city_summary['MeanOpportunityScore'], width, label='Mean Opportunity Score', color='#0284c7', alpha=0.9)
ax1.set_ylabel('Mean Regional Opportunity Score', color='#0284c7', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#0284c7')
ax1.set_xticks(x)
ax1.set_xticklabels(city_summary['City'], rotation=30, ha='right', fontsize=10, fontweight='bold')

ax2 = ax1.twinx()
rects2 = ax2.bar(x + width/2, city_summary['TotalDemand'] / 1000.0, width, label='Total Demand (k)', color='#f59e0b', alpha=0.85)
ax2.set_ylabel('Total Search Demand (Thousands)', color='#d97706', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='#d97706')
ax2.grid(False)

plt.title("Aggregated Opportunity Score vs. Total Demand by Metro Cluster", fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
chart3_path = os.path.join(CHARTS_DIR, "03_city_opportunity_and_demand.png")
plt.savefig(chart3_path, dpi=300)
plt.close()
print(f"[SAVED] {chart3_path}")

# -------------------------------------------------------------
# CHART 4: Revenue Potential Distribution Across Cities
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 6.5), dpi=300)
order = df.groupby('City')['EstimatedRevenuePotential'].median().sort_values(ascending=False).index
sns.boxplot(
    data=df,
    x='City',
    y='EstimatedRevenuePotential',
    order=order,
    palette='Spectral',
    ax=ax,
    fliersize=3,
    linewidth=1.2
)
ax.set_title("Distribution of Estimated Market Revenue Potential (INR) by City", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("City", fontsize=12, fontweight='bold')
ax.set_ylabel("Est. Monthly Revenue Potential (INR in Crores)", fontsize=12, fontweight='bold')
# format y axis in Crores (1 Cr = 1e7)
import matplotlib.ticker as ticker
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"INR {y/1e7:.1f} Cr"))
plt.xticks(rotation=30, ha='right', fontweight='bold')
plt.tight_layout()
chart4_path = os.path.join(CHARTS_DIR, "04_revenue_potential_distribution.png")
plt.savefig(chart4_path, dpi=300)
plt.close()
print(f"[SAVED] {chart4_path}")

# -------------------------------------------------------------
# CHART 5: Population Segment Comparison (CAC, Conversion & Demand)
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)
segment_order = ['Student', 'Early Career', 'Professional']

# 1. Lead Conversion Rate
sns.barplot(data=df, x='PopulationSegment', y='LeadConversionRate', order=segment_order, ax=axes[0], palette='Blues_d', errorbar=None)
axes[0].set_title("Avg. Lead Conversion Rate", fontweight='bold', fontsize=12)
axes[0].set_ylabel("Conversion Rate (%)", fontweight='bold')
axes[0].yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))

# 2. Estimated CAC
sns.barplot(data=df, x='PopulationSegment', y='EstimatedAcquisitionCostINR', order=segment_order, ax=axes[1], palette='Oranges_d', errorbar=None)
axes[1].set_title("Avg. Acquisition Cost (INR)", fontweight='bold', fontsize=12)
axes[1].set_ylabel("CAC (INR)", fontweight='bold')

# 3. Opportunity Score
sns.barplot(data=df, x='PopulationSegment', y='OpportunityScore', order=segment_order, ax=axes[2], palette='Greens_d', errorbar=None)
axes[2].set_title("Avg. Opportunity Score", fontweight='bold', fontsize=12)
axes[2].set_ylabel("Opportunity Score", fontweight='bold')

for ax in axes:
    ax.set_xlabel("Population Segment", fontweight='bold')

plt.suptitle("Demographic Segment Performance Across 400 Regional Micro-Markets", fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
chart5_path = os.path.join(CHARTS_DIR, "05_population_segment_breakdown.png")
plt.savefig(chart5_path, dpi=300)
plt.close()
print(f"[SAVED] {chart5_path}")

# -------------------------------------------------------------
# CHART 6: Correlation Matrix of Geospatial & Financial Metrics
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 7), dpi=300)
numeric_cols = [
    'MonthlySearchDemand', 'ExistingCompetitors', 'MedianAnnualIncomeINR',
    'LeadConversionRate', 'EstimatedAcquisitionCostINR', 'OpportunityScore',
    'EstimatedRevenuePotential'
]
corr = df[numeric_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr,
    mask=mask,
    annot=True,
    fmt=".2f",
    cmap='coolwarm',
    vmin=-0.8,
    vmax=0.8,
    square=True,
    linewidths=0.75,
    cbar_kws={"shrink": 0.8},
    ax=ax
)
ax.set_title("Correlation Matrix of Market Metrics", fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
chart6_path = os.path.join(CHARTS_DIR, "06_correlation_matrix.png")
plt.savefig(chart6_path, dpi=300)
plt.close()
print(f"[SAVED] {chart6_path}")

# =============================================================
# 3. INTERACTIVE FOLIUM MAP GENERATION
# =============================================================
print("\n[INFO] Generating interactive Folium map...")

# Center map on geographical center of India
india_center = [20.5937, 78.9629]
m = folium.Map(
    location=india_center,
    zoom_start=5,
    tiles='OpenStreetMap',
    control_scale=True
)

# 1. HeatMap Layer of Search Demand
heat_data = [[row['Latitude'], row['Longitude'], row['MonthlySearchDemand']] for _, row in df.iterrows()]
demand_heatmap = HeatMap(
    heat_data,
    name='Monthly Search Demand Heatmap',
    min_opacity=0.25,
    max_zoom=18,
    radius=22,
    blur=16,
    show=False
)
demand_heatmap.add_to(m)

# 2. MarkerCluster Layer for Micro-Regions
cluster = MarkerCluster(
    name='All Regional Micro-Markets (Clustered)',
    overlay=True,
    control=True,
    show=True
)

# Helper function for Opportunity Score Color Scale
def get_score_color(score):
    if score >= 100:
        return '#d90429'  # Ultra-high opportunity (Ruby Red)
    elif score >= 60:
        return '#f77f00'  # High opportunity (Amber Orange)
    elif score >= 30:
        return '#0284c7'  # Moderate opportunity (Sky Blue)
    else:
        return '#64748b'  # Saturated / Low opportunity (Slate Grey)

for _, row in df.iterrows():
    # Calculate radius proportional to demand
    radius = 4 + (row['MonthlySearchDemand'] / 350.0)
    color = get_score_color(row['OpportunityScore'])
    
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 12px; width: 260px; line-height: 1.4; color: #1e293b;">
        <div style="background-color: #1e293b; color: white; padding: 8px 10px; border-radius: 4px 4px 0 0; font-weight: bold; font-size: 13px;">
            📍 {row['RegionID']} - {row['City']}, {row['State']}
        </div>
        <div style="padding: 10px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 4px 4px; background-color: #ffffff;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="color: #64748b; padding: 2px 0;">Segment:</td><td style="font-weight: bold; text-align: right;">{row['PopulationSegment']}</td></tr>
                <tr><td style="color: #64748b; padding: 2px 0;">Monthly Demand:</td><td style="font-weight: bold; text-align: right; color: #0369a1;">{row['MonthlySearchDemand']:,}</td></tr>
                <tr><td style="color: #64748b; padding: 2px 0;">Competitor Count:</td><td style="font-weight: bold; text-align: right; color: {'#dc2626' if row['ExistingCompetitors'] > 10 else '#16a34a'};">{row['ExistingCompetitors']}</td></tr>
                <tr><td style="color: #64748b; padding: 2px 0;">Conversion Rate:</td><td style="font-weight: bold; text-align: right;">{row['LeadConversionRate']:.2%}</td></tr>
                <tr><td style="color: #64748b; padding: 2px 0;">Estimated CAC:</td><td style="font-weight: bold; text-align: right;">₹{row['EstimatedAcquisitionCostINR']}</td></tr>
                <tr><td style="color: #64748b; padding: 2px 0;">Median Income:</td><td style="font-weight: bold; text-align: right;">₹{row['MedianAnnualIncomeINR']:,}</td></tr>
                <tr style="border-top: 1px dashed #cbd5e1;"><td style="color: #0f172a; padding: 5px 0 2px 0; font-weight: bold;">Opportunity Score:</td><td style="font-weight: 800; font-size: 13px; text-align: right; color: {color};">{row['OpportunityScore']:.2f}</td></tr>
                <tr><td style="color: #64748b; padding: 2px 0;">Est. Monthly Rev:</td><td style="font-weight: bold; text-align: right; color: #059669;">₹{row['EstimatedRevenuePotential']:,.0f}</td></tr>
            </table>
        </div>
    </div>
    """
    
    circle = folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=radius,
        color=color,
        weight=1.5,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{row['RegionID']} | {row['City']} | Score: {row['OpportunityScore']:.1f}"
    )
    circle.add_to(cluster)

cluster.add_to(m)

# 3. Dedicated Callout Pin Markers for Top 3 Underserved Regions
top_3_group = folium.FeatureGroup(name='🌟 Top 3 High-Potential Underserved Regions (Callouts)', show=True)

rank_colors = {1: '#d90429', 2: '#e65100', 3: '#2e7d32'}
rank_icons = {1: 'trophy', 2: 'star', 3: 'bullseye'}

for rank, (_, row) in enumerate(top_3_regions.iterrows(), 1):
    callout_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 12px; width: 290px; line-height: 1.4; color: #0f172a;">
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); color: #fbbf24; padding: 10px; border-radius: 6px 6px 0 0; font-weight: bold; font-size: 14px; border-bottom: 2px solid #fbbf24;">
            🏆 PRIORITY TARGET #{rank}: {row['City']} ({row['RegionID']})
        </div>
        <div style="padding: 12px; border: 1px solid #cbd5e1; border-top: none; border-radius: 0 0 6px 6px; background-color: #f8fafc;">
            <p style="margin: 0 0 8px 0; font-size: 12px; color: #334155;">
                <strong>Location:</strong> {row['City']}, {row['State']}<br>
                <strong>Coordinates:</strong> {row['Latitude']:.4f}°N, {row['Longitude']:.4f}°E<br>
                <strong>Target Segment:</strong> {row['PopulationSegment']}
            </p>
            <table style="width: 100%; border-collapse: collapse; font-size: 11.5px; background: white; padding: 6px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding: 4px 6px; color: #64748b;">Monthly Search Demand:</td><td style="padding: 4px 6px; font-weight: bold; color: #0369a1; text-align: right;">{row['MonthlySearchDemand']:,}</td></tr>
                <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding: 4px 6px; color: #64748b;">Existing Competitors:</td><td style="padding: 4px 6px; font-weight: bold; color: #16a34a; text-align: right;">{row['ExistingCompetitors']} only</td></tr>
                <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding: 4px 6px; color: #64748b;">Lead Conversion Rate:</td><td style="padding: 4px 6px; font-weight: bold; text-align: right;">{row['LeadConversionRate']:.2%}</td></tr>
                <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding: 4px 6px; color: #64748b;">Estimated CAC:</td><td style="padding: 4px 6px; font-weight: bold; text-align: right;">₹{row['EstimatedAcquisitionCostINR']}</td></tr>
                <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding: 4px 6px; color: #64748b;">Median Annual Income:</td><td style="padding: 4px 6px; font-weight: bold; text-align: right;">₹{row['MedianAnnualIncomeINR']:,}</td></tr>
                <tr style="background: #fef3c7; font-weight: bold;"><td style="padding: 5px 6px; color: #92400e;">Opportunity Score:</td><td style="padding: 5px 6px; font-weight: 800; font-size: 13px; color: #b45309; text-align: right;">{row['OpportunityScore']:.2f}</td></tr>
            </table>
            <div style="margin-top: 8px; font-size: 11px; background: #ecfdf5; border-left: 3px solid #10b981; padding: 6px; color: #065f46;">
                <strong>Recommendation:</strong> Prime territory for immediate acquisition blitz. High unmet organic demand with minimal incumbent resistance.
            </div>
        </div>
    </div>
    """
    
    # Custom pin marker
    marker = folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(callout_html, max_width=320),
        tooltip=f"★ RANK #{rank}: {row['City']} ({row['RegionID']}) | Score: {row['OpportunityScore']:.1f}",
        icon=folium.Icon(color='red' if rank == 1 else 'orange' if rank == 2 else 'green', icon='info-sign', prefix='glyphicon')
    )
    marker.add_to(top_3_group)
    
    # Highlight circle around top 3
    folium.Circle(
        location=[row['Latitude'], row['Longitude']],
        radius=14000,
        color=rank_colors[rank],
        weight=2.5,
        fill=True,
        fill_color=rank_colors[rank],
        fill_opacity=0.18,
        dash_array='5, 5'
    ).add_to(top_3_group)

top_3_group.add_to(m)

# 4. Floating Legend & HUD Controls
legend_html = """
<div style="
    position: fixed; 
    bottom: 30px; 
    left: 30px; 
    width: 290px; 
    background-color: rgba(255, 255, 255, 0.95);
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    z-index: 9999;
    font-size: 12px;
    font-family: Arial, sans-serif;
    padding: 12px 14px;
    line-height: 1.4;
    color: #1e293b;
">
    <div style="font-weight: bold; font-size: 13px; margin-bottom: 6px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; color: #0f172a;">
        🗺️ Regional Market Opportunity Legend
    </div>
    <div style="margin-bottom: 8px; font-size: 11px; color: #64748b;">
        <code>Opportunity = (Demand × Conversion) / (Competitors + 1)</code>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;">
        <span style="height: 12px; width: 12px; background-color: #d90429; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
        <span><strong>Ultra High Opportunity</strong> (Score ≥ 100)</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;">
        <span style="height: 12px; width: 12px; background-color: #f77f00; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
        <span><strong>High Opportunity</strong> (60 ≤ Score < 100)</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;">
        <span style="height: 12px; width: 12px; background-color: #0284c7; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
        <span><strong>Moderate Opportunity</strong> (30 ≤ Score < 60)</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 8px;">
        <span style="height: 12px; width: 12px; background-color: #64748b; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
        <span><strong>Saturated / Lower Yield</strong> (Score < 30)</span>
    </div>
    <div style="border-top: 1px solid #e2e8f0; padding-top: 6px; font-size: 11px; color: #475569;">
        <strong>Marker Size:</strong> Proportional to Monthly Search Volume<br>
        <strong>Pins:</strong> Dedicated Top 3 Underserved Hubs
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Add Layer Control
folium.LayerControl(collapsed=False).add_to(m)

# Save Folium Map
m.save(MAP_OUTPUT_PATH)
print(f"[SAVED] Standalone interactive map: {MAP_OUTPUT_PATH}")

print("\n[SUCCESS] Visualizations and Folium Map pipeline executed successfully!")
