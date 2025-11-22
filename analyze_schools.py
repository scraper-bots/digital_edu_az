import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from collections import Counter
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set style for better-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Create charts directory if it doesn't exist
os.makedirs('charts', exist_ok=True)

# Load the data
print("Loading data...")
df = pd.read_csv('schools.csv')

print(f"Total schools in dataset: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")

# Basic statistics
print("\n" + "="*50)
print("BASIC STATISTICS")
print("="*50)
print(f"Total number of schools: {len(df)}")
print(f"Number of regions: {df['regionName'].nunique()}")
print(f"Number of unique school types: {df['schoolType'].nunique()}")
print(f"Number of unique school kinds: {df['schoolKind'].nunique()}")

# 1. SCHOOLS DISTRIBUTION BY REGION
print("\n\nGenerating Chart 1: Schools Distribution by Region...")
region_counts = df['regionName'].value_counts().head(20)

fig, ax = plt.subplots(figsize=(14, 10))
bars = ax.barh(range(len(region_counts)), region_counts.values, color='#2E86AB')
ax.set_yticks(range(len(region_counts)))
ax.set_yticklabels(region_counts.index, fontsize=11)
ax.set_xlabel('Number of Schools', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Regions by Number of Schools', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels on bars
for i, (idx, value) in enumerate(region_counts.items()):
    ax.text(value + 5, i, str(value), va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_schools_by_region.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/01_schools_by_region.png")

# Statistics for regions
print(f"\nTop 5 regions:")
for region, count in region_counts.head(5).items():
    percentage = (count / len(df)) * 100
    print(f"  - {region}: {count} schools ({percentage:.1f}%)")

# 2. SCHOOLS BY TYPE
print("\n\nGenerating Chart 2: Schools by Type...")
type_counts = df['schoolType'].value_counts()

# Create better readable horizontal bar chart
fig, ax = plt.subplots(figsize=(14, 10))
colors = sns.color_palette("Set2", len(type_counts))

# Create horizontal bars
bars = ax.barh(range(len(type_counts)), type_counts.values, color=colors)
ax.set_yticks(range(len(type_counts)))
ax.set_yticklabels(type_counts.index, fontsize=12)
ax.set_xlabel('Number of Schools', fontsize=13, fontweight='bold')
ax.set_title('Distribution of Schools by Type', fontsize=15, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels and percentages on bars
for i, (school_type, value) in enumerate(type_counts.items()):
    percentage = (value / len(df)) * 100
    # Position label at the end of bar
    ax.text(value + 30, i, f'{value} ({percentage:.1f}%)',
            va='center', fontsize=11, fontweight='bold')

# Add grid for better readability
ax.xaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('charts/02_schools_by_type.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/02_schools_by_type.png")

print(f"\nSchool types breakdown:")
for school_type, count in type_counts.items():
    percentage = (count / len(df)) * 100
    print(f"  - {school_type}: {count} schools ({percentage:.1f}%)")

# 3. SCHOOL KIND DISTRIBUTION
print("\n\nGenerating Chart 3: School Kind Distribution...")
kind_counts = df['schoolKind'].value_counts()

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.bar(range(len(kind_counts)), kind_counts.values, color='#06A77D')
ax.set_xticks(range(len(kind_counts)))
ax.set_xticklabels(kind_counts.index, rotation=45, ha='right', fontsize=11)
ax.set_ylabel('Number of Schools', fontsize=12, fontweight='bold')
ax.set_title('Distribution by School Kind (Education Level)', fontsize=14, fontweight='bold', pad=20)

# Add value labels on bars
for i, value in enumerate(kind_counts.values):
    ax.text(i, value + 10, str(value), ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/03_schools_by_kind.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/03_schools_by_kind.png")

print(f"\nSchool kinds breakdown:")
for kind, count in kind_counts.items():
    percentage = (count / len(df)) * 100
    print(f"  - {kind}: {count} schools ({percentage:.1f}%)")

# 4. DIGITAL ADOPTION (hasJurnal, hasMeeting)
print("\n\nGenerating Chart 4: Digital Features Adoption...")
digital_features = {
    'E-Journal System': df['hasJurnal'].sum(),
    'Online Meeting System': df['hasMeeting'].sum(),
    'Both Features': ((df['hasJurnal'] == True) & (df['hasMeeting'] == True)).sum(),
    'No Digital Features': ((df['hasJurnal'] == False) & (df['hasMeeting'] == False)).sum()
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Pie chart for digital features
colors_digital = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
wedges, texts, autotexts = ax1.pie(digital_features.values(),
                                     labels=digital_features.keys(),
                                     autopct='%1.1f%%',
                                     colors=colors_digital,
                                     startangle=90,
                                     textprops={'fontsize': 10})
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax1.set_title('Digital Features Adoption Overview', fontsize=13, fontweight='bold')

# Bar chart comparison
features_comparison = {
    'Has E-Journal': [df['hasJurnal'].sum(), len(df) - df['hasJurnal'].sum()],
    'Has Online Meetings': [df['hasMeeting'].sum(), len(df) - df['hasMeeting'].sum()]
}

x = np.arange(len(features_comparison))
width = 0.35

bars1 = ax2.bar(x - width/2, [features_comparison['Has E-Journal'][0], features_comparison['Has Online Meetings'][0]],
                width, label='Enabled', color='#06A77D')
bars2 = ax2.bar(x + width/2, [features_comparison['Has E-Journal'][1], features_comparison['Has Online Meetings'][1]],
                width, label='Disabled', color='#D62839')

ax2.set_ylabel('Number of Schools', fontsize=11, fontweight='bold')
ax2.set_title('Digital Features: Enabled vs Disabled', fontsize=13, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(['E-Journal', 'Online Meetings'])
ax2.legend()

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/04_digital_adoption.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/04_digital_adoption.png")

# Digital adoption statistics
total_schools = len(df)
print(f"\nDigital adoption rates:")
print(f"  - E-Journal system: {df['hasJurnal'].sum()} schools ({(df['hasJurnal'].sum()/total_schools)*100:.1f}%)")
print(f"  - Online meetings: {df['hasMeeting'].sum()} schools ({(df['hasMeeting'].sum()/total_schools)*100:.1f}%)")
print(f"  - Both features: {digital_features['Both Features']} schools ({(digital_features['Both Features']/total_schools)*100:.1f}%)")
print(f"  - No digital features: {digital_features['No Digital Features']} schools ({(digital_features['No Digital Features']/total_schools)*100:.1f}%)")

# 5. GEOGRAPHIC DISTRIBUTION
print("\n\nGenerating Chart 5: Geographic Distribution...")
# Filter schools with valid coordinates
df_with_coords = df[(df['lat'] != 0) & (df['lng'] != 0) &
                     (df['lat'].notna()) & (df['lng'].notna())]

fig, ax = plt.subplots(figsize=(14, 10))

# Create scatter plot
scatter = ax.scatter(df_with_coords['lng'], df_with_coords['lat'],
                     c=df_with_coords['hasJurnal'].astype(int),
                     cmap='RdYlGn', alpha=0.6, s=50, edgecolors='black', linewidth=0.5)

ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
ax.set_title(f'Geographic Distribution of Schools (n={len(df_with_coords)})\nColored by E-Journal Adoption',
             fontsize=14, fontweight='bold', pad=20)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Has E-Journal', fontsize=11, fontweight='bold')
cbar.set_ticks([0, 1])
cbar.set_ticklabels(['No', 'Yes'])

plt.tight_layout()
plt.savefig('charts/05_geographic_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/05_geographic_distribution.png")

print(f"\nGeographic data availability:")
print(f"  - Schools with coordinates: {len(df_with_coords)} ({(len(df_with_coords)/total_schools)*100:.1f}%)")
print(f"  - Schools without coordinates: {total_schools - len(df_with_coords)} ({((total_schools - len(df_with_coords))/total_schools)*100:.1f}%)")

# 6. CONTACT INFORMATION COMPLETENESS
print("\n\nGenerating Chart 6: Contact Information Completeness...")
contact_completeness = {
    'Has Email': df['contacts_emails'].notna().sum(),
    'Has Phone': df['contacts_phones'].notna().sum(),
    'Has Website': df['siteUrl'].notna().sum(),
    'Has All Contact Info': ((df['contacts_emails'].notna()) &
                              (df['contacts_phones'].notna()) &
                              (df['siteUrl'].notna())).sum(),
    'Missing Contact Info': ((df['contacts_emails'].isna()) |
                              (df['contacts_phones'].isna())).sum()
}

fig, ax = plt.subplots(figsize=(12, 8))
categories = list(contact_completeness.keys())
values = list(contact_completeness.values())
colors_contact = ['#2E86AB', '#06A77D', '#F18F01', '#A23B72', '#D62839']

bars = ax.barh(categories, values, color=colors_contact)
ax.set_xlabel('Number of Schools', fontsize=12, fontweight='bold')
ax.set_title('Contact Information Completeness', fontsize=14, fontweight='bold', pad=20)

# Add value labels and percentages
for i, (bar, value) in enumerate(zip(bars, values)):
    percentage = (value / total_schools) * 100
    ax.text(value + 20, bar.get_y() + bar.get_height()/2,
            f'{value} ({percentage:.1f}%)',
            va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_contact_completeness.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/06_contact_completeness.png")

print(f"\nContact information statistics:")
for category, count in contact_completeness.items():
    percentage = (count / total_schools) * 100
    print(f"  - {category}: {count} schools ({percentage:.1f}%)")

# 7. REGIONAL DIGITAL ADOPTION HEATMAP
print("\n\nGenerating Chart 7: Regional Digital Adoption Analysis...")
# Get top 15 regions by school count
top_regions = df['regionName'].value_counts().head(15).index

# Calculate digital adoption rates by region
regional_digital = []
for region in top_regions:
    region_df = df[df['regionName'] == region]
    total = len(region_df)
    journal_rate = (region_df['hasJurnal'].sum() / total) * 100
    meeting_rate = (region_df['hasMeeting'].sum() / total) * 100
    regional_digital.append({
        'Region': region,
        'E-Journal %': journal_rate,
        'Online Meeting %': meeting_rate,
        'Total Schools': total
    })

regional_df = pd.DataFrame(regional_digital)

fig, ax = plt.subplots(figsize=(14, 10))

x = np.arange(len(regional_df))
width = 0.35

bars1 = ax.bar(x - width/2, regional_df['E-Journal %'], width, label='E-Journal Adoption %', color='#2E86AB')
bars2 = ax.bar(x + width/2, regional_df['Online Meeting %'], width, label='Online Meeting Adoption %', color='#F18F01')

ax.set_ylabel('Adoption Rate (%)', fontsize=12, fontweight='bold')
ax.set_xlabel('Region', fontsize=12, fontweight='bold')
ax.set_title('Digital Features Adoption by Top 15 Regions', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(regional_df['Region'], rotation=45, ha='right', fontsize=10)
ax.legend(fontsize=11)
ax.set_ylim(0, 105)

# Add grid for better readability
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('charts/07_regional_digital_adoption.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/07_regional_digital_adoption.png")

# 8. ADMINISTRATION HIERARCHY
print("\n\nGenerating Chart 8: Schools by Administrative Subjection...")
subjection_counts = df['subjection'].value_counts()

fig, ax = plt.subplots(figsize=(14, 10))
colors_subj = sns.color_palette("Set2", len(subjection_counts))
bars = ax.barh(range(len(subjection_counts)), subjection_counts.values, color=colors_subj)
ax.set_yticks(range(len(subjection_counts)))
ax.set_yticklabels(subjection_counts.index, fontsize=11)
ax.set_xlabel('Number of Schools', fontsize=12, fontweight='bold')
ax.set_title('Schools by Administrative Subjection', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels
for i, value in enumerate(subjection_counts.values):
    percentage = (value / total_schools) * 100
    ax.text(value + 10, i, f'{value} ({percentage:.1f}%)',
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/08_administrative_subjection.png', dpi=300, bbox_inches='tight')
plt.close()
print("[DONE] Chart saved: charts/08_administrative_subjection.png")

print(f"\nAdministrative subjection breakdown:")
for subjection, count in subjection_counts.items():
    percentage = (count / total_schools) * 100
    print(f"  - {subjection}: {count} schools ({percentage:.1f}%)")

print("\n" + "="*50)
print("ALL CHARTS GENERATED SUCCESSFULLY!")
print("="*50)
print(f"\nTotal charts created: 8")
print("All charts saved in 'charts/' folder")
print("\nKey Insights Summary:")
print(f"1. Total schools analyzed: {total_schools}")
print(f"2. Coverage across {df['regionName'].nunique()} regions")
print(f"3. Digital adoption: {(df['hasJurnal'].sum()/total_schools)*100:.1f}% have e-journal")
print(f"4. Geographic data available for {(len(df_with_coords)/total_schools)*100:.1f}% of schools")
print(f"5. Contact completeness varies significantly across schools")
