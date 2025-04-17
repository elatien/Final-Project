# analyze.py
# we used chatGPT to help with visuals using seaborn and to get debugging help and structure of code
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Styling
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# Connect to the database
conn = sqlite3.connect("FINALPROJECTDB.db")

# --- JOIN + INCOME + EDUCATION + RATINGS ---
query = """
SELECT 
    income.zip_code AS zip,
    income.median_income,
    education.high_school_or_higher AS high_school,
    education.bachelors_degree_or_higher AS bachelors,
    education.graduate_or_professional_degree AS graduate,
    AVG(restaurants.rating) AS avg_rating,
    SUM(restaurants.review_count) AS total_reviews,
    COUNT(restaurants.id) AS restaurant_count
FROM income
JOIN education ON income.zip_code = education.zip_code
JOIN restaurants ON income.zip_code = restaurants.zip_code
GROUP BY income.zip_code
ORDER BY income.zip_code;
"""

# Load data into DataFrame
df = pd.read_sql_query(query, conn)

# Write calculation results to text file
with open("calculated_data.txt", "w") as f:
    f.write("Joined Data (Income, Education, Restaurant Ratings) by ZIP (Ann Arbor Only):\n\n")
    f.write(df[df["zip"].isin(["48103", "48104", "48105", "48108", "48109"])]
            .to_string(index=False))

# Filter to Ann Arbor ZIP codes
ann_arbor_zips = ["48103", "48104", "48105", "48108", "48109"]
df = df[df["zip"].isin(ann_arbor_zips)]
conn.close()

# --- VISUALIZATION 1: Education Attainment by ZIP ---
edu_melt = df.melt(
    id_vars='zip',
    value_vars=['high_school', 'bachelors', 'graduate'],
    var_name='education_level',
    value_name='percent'
)

sns.barplot(data=edu_melt, x='education_level', y='percent', hue='zip')
plt.title("Education Attainment by ZIP (Ann Arbor Only)")
plt.ylabel("Percentage of Population")
plt.xlabel("Education Level")
plt.tight_layout()
plt.savefig("viz_education_by_zip.png")
plt.show()

# --- VISUALIZATION 2: Income vs. Restaurant Ratings by ZIP ---
sns.scatterplot(data=df, x='median_income', y='avg_rating', hue='zip', s=150)
plt.title("Income vs. Restaurant Ratings (Ann Arbor Only)")
plt.xlabel("Median Income ($)")
plt.ylabel("Average Yelp Rating")
plt.xlim(left=0)  # ensure positive x-axis
plt.legend(title="ZIP Code", loc='best', ncol=2)
plt.tight_layout()
plt.savefig("viz_income_vs_rating.png")
plt.show()

# --- SIMPLIFIED: Use ZIP directly for Bachelor's-based plots ---
sns.barplot(data=df, x='zip', y='avg_rating')
plt.title("Avg Yelp Rating by ZIP (Sorted by Bachelor's Degree %)")
plt.xlabel("ZIP Code")
plt.ylabel("Average Yelp Rating")
plt.tight_layout()
plt.savefig("viz_bachelors_rating_bar.png")
plt.show()

sns.barplot(data=df, x='zip', y='total_reviews')
plt.title("Total Yelp Reviews by ZIP (Sorted by Bachelor's Degree %)")
plt.xlabel("ZIP Code")
plt.ylabel("Total Yelp Reviews")
plt.tight_layout()
plt.savefig("viz_bachelors_reviews_bar.png")
plt.show()

# --- VISUALIZATION 5: Avg Rating by Education Level and ZIP ---
edu_rating_df = df[['zip', 'avg_rating', 'high_school', 'bachelors', 'graduate']]
edu_rating_melt = edu_rating_df.melt(
    id_vars=['zip', 'avg_rating'],
    value_vars=['high_school', 'bachelors', 'graduate'],
    var_name='education_level',
    value_name='education_percent'
)

sns.barplot(
    data=edu_rating_melt,
    x='education_level',
    y='avg_rating',
    hue='zip'
)
plt.title("Average Yelp Rating by Education Level and ZIP (Ann Arbor Only)")
plt.xlabel("Education Level")
plt.ylabel("Average Yelp Rating")
plt.tight_layout()
plt.savefig("viz_avg_rating_by_edu_and_zip.png")
plt.show()
