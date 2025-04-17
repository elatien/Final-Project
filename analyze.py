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

# Calculation
bracket_query = """
SELECT 
    CASE
        WHEN income.median_income < 50000 THEN '<50k'
        WHEN income.median_income BETWEEN 50000 AND 74999 THEN '50–75k'
        WHEN income.median_income BETWEEN 75000 AND 99999 THEN '75–100k'
        ELSE '100k+'
    END AS income_bracket,
    ROUND(1.0 * SUM(restaurants.review_count) / COUNT(restaurants.id), 2) AS avg_reviews_per_restaurant,
    COUNT(DISTINCT income.zip_code) AS zip_count
FROM income
JOIN education ON income.zip_code = education.zip_code
JOIN restaurants ON income.zip_code = restaurants.zip_code
GROUP BY income_bracket
ORDER BY income_bracket;
"""

bracket_df = pd.read_sql_query(bracket_query, conn)

# Save to text file
with open("calculated_data.txt", "w") as f:
    f.write("Average Yelp Reviews per Restaurant by Income Bracket:\n\n")
    f.write(bracket_df.to_string(index=False))

# Full Join by ZIP 
main_query = """
SELECT 
    income.zip_code AS zip,
    income.median_income,
    education.high_school AS high_school,
    education.bachelors AS bachelors,
    education.graduate AS graduate,
    AVG(restaurants.rating) AS avg_rating,
    SUM(restaurants.review_count) AS total_reviews,
    COUNT(restaurants.id) AS restaurant_count
FROM income
JOIN education ON income.zip_code = education.zip_code
JOIN restaurants ON income.zip_code = restaurants.zip_code
GROUP BY income.zip_code
ORDER BY income.zip_code;
"""

df = pd.read_sql_query(main_query, conn)
conn.close()

# Only Ann Arbor ZIP codes
ann_arbor_zips = ["48103", "48104", "48105", "48108", "48109"]
df = df[df["zip"].isin(ann_arbor_zips)]

# Education Attainment by ZIP 
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

# Income vs. Restaurant Ratings by ZIP
sns.scatterplot(data=df, x='median_income', y='avg_rating', hue='zip', s=150)
plt.title("Income vs. Restaurant Ratings (Ann Arbor Only)")
plt.xlabel("Median Income ($)")
plt.ylabel("Average Yelp Rating")
plt.xlim(left=0)  # ensure positive x-axis
plt.legend(title="ZIP Code", loc='best', ncol=2)
plt.tight_layout()
plt.savefig("viz_income_vs_rating.png")
plt.show()

# Avg Yelp Rating by ZIP
sns.barplot(data=df, x='zip', y='avg_rating')
plt.title("Avg Yelp Rating by ZIP (Sorted by Bachelor's Degree %)")
plt.xlabel("ZIP Code")
plt.ylabel("Average Yelp Rating")
plt.tight_layout()
plt.savefig("viz_bachelors_rating_bar.png")
plt.show()

# Total Reviews by ZIP
sns.barplot(data=df, x='zip', y='total_reviews')
plt.title("Total Yelp Reviews by ZIP (Sorted by Bachelor's Degree %)")
plt.xlabel("ZIP Code")
plt.ylabel("Total Yelp Reviews")
plt.tight_layout()
plt.savefig("viz_bachelors_reviews_bar.png")
plt.show()

# Avg Rating by Education Level and ZIP
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
