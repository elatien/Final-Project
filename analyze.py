# analyze.py

import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Styling
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# Connect to database
conn = sqlite3.connect("FINALPROJECTDB.db")

# Load data
income_df = pd.read_sql_query("SELECT * FROM income", conn)
income_df = income_df[['zip_code', 'median_income']]
income_df = income_df.rename(columns={'zip_code': 'zip'})


edu_df = pd.read_sql_query("SELECT * FROM education", conn)
edu_df.columns = ['zip', 'high_school', 'bachelors', 'graduate']

yelp_df = pd.read_sql_query("SELECT * FROM restaurants", conn)
yelp_df.columns = ['id', 'name', 'rating', 'review_count', 'zip']

# Aggregate Yelp data by ZIP
yelp_agg = yelp_df.groupby('zip').agg(
    avg_rating=('rating', 'mean'),
    total_reviews=('review_count', 'sum'),
    restaurant_count=('id', 'count')
).reset_index()

# Merge all data
merged_df = income_df.merge(edu_df, on='zip').merge(yelp_agg, on='zip')

conn.close()

### Visualization 1: Income vs. Average Restaurant Rating
sns.scatterplot(data=merged_df, x='median_income', y='avg_rating', hue='zip', s=150)
plt.title('Income vs. Restaurant Ratings by ZIP')
plt.xlabel('Median Income ($)')
plt.ylabel('Average Yelp Rating')
plt.tight_layout()
plt.savefig("viz_income_vs_rating.png")
plt.show()

### Visualization 2: Education Levels by ZIP
edu_melt = merged_df.melt(
    id_vars=['zip'],
    value_vars=['high_school', 'bachelors', 'graduate'],
    var_name='education_level',
    value_name='percent'
)

sns.barplot(data=edu_melt, x='education_level', y='percent', hue='zip')
plt.title('Education Attainment by ZIP')
plt.ylabel('Percentage of Population')
plt.xlabel('Education Level')
plt.tight_layout()
plt.savefig("viz_education_by_zip.png")
plt.show()

### Visualization 3: Bachelor’s % vs. Total Yelp Reviews
sns.regplot(data=merged_df, x='bachelors', y='total_reviews')
plt.title("Bachelor's Degree % vs. Total Restaurant Reviews")
plt.xlabel('Percent with Bachelor’s Degree')
plt.ylabel('Total Yelp Reviews')
plt.tight_layout()
plt.savefig("viz_bachelors_vs_reviews.png")
plt.show()

sns.regplot(data=merged_df, x='bachelors', y='avg_rating')
plt.title("Bachelor’s Degree % vs. Average Yelp Rating")
plt.xlabel('Percent with Bachelor’s Degree')
plt.ylabel('Average Restaurant Rating')
plt.tight_layout()
plt.savefig("viz_bachelors_vs_avg_rating.png")
plt.show()

# Create a copy of merged data with education + average rating
edu_rating_df = merged_df[['zip', 'avg_rating', 'high_school', 'bachelors', 'graduate']]

# Melt the education columns into rows so we can group by ZIP and education level
edu_rating_melt = edu_rating_df.melt(
    id_vars=['zip', 'avg_rating'],
    value_vars=['high_school', 'bachelors', 'graduate'],
    var_name='education_level',
    value_name='education_percent'
)

# Plot
sns.barplot(
    data=edu_rating_melt,
    x='education_level',
    y='avg_rating',
    hue='zip'
)
plt.title("Average Yelp Rating by Education Level and ZIP")
plt.xlabel("Education Level")
plt.ylabel("Average Yelp Rating")
plt.tight_layout()
plt.savefig("viz_avg_rating_by_edu_and_zip.png")
plt.show()
