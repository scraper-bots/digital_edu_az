import pandas as pd
import sys
import io

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

df = pd.read_csv('schools.csv')

print('School Type counts:')
print(df['schoolType'].value_counts())
print(f'\nTotal unique types: {df["schoolType"].nunique()}')
