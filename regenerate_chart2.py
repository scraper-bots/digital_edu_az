import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import io

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set style
sns.set_style("whitegrid")

# Load data
print("Loading data...")
df = pd.read_csv('schools.csv')

# Generate Chart 2: Schools by Type
print("Generating improved Chart 2: Schools by Type...")
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

print("[DONE] Chart 2 regenerated successfully!")
print(f"\nSchool types breakdown:")
for school_type, count in type_counts.items():
    percentage = (count / len(df)) * 100
    print(f"  - {school_type}: {count} schools ({percentage:.1f}%)")
