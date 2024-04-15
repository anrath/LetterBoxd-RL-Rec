import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('users_export.csv')

# Convert 'display_name' to string and fill missing values with a placeholder
df['display_name'] = df['display_name'].fillna('Unknown').astype(str)

# Basic data summary
print(df.describe())

# Sample a subset for visualization 
sampled_df = df.sample(n=40, random_state=42)
sampled_df2 = df.sample(n=1000, random_state=42)

# Visualization 1: Bar chart of the number of ratings pages per user
plt.figure(figsize=(10, 6))
plt.bar(sampled_df['display_name'], sampled_df['num_ratings_pages'], color='skyblue')
plt.xlabel('User')
plt.ylabel('Number of Ratings Pages')
plt.xticks(rotation=45, ha="right")
plt.title('Number of Ratings Pages per User')
plt.tight_layout()
plt.show()

# Visualization 2: Histogram of the number of reviews
plt.figure(figsize=(10, 6))
plt.hist(df['num_reviews'], bins=20, color='skyblue', range=(0, 6000))
plt.xlabel('Number of Reviews')
plt.ylabel('Frequency')
plt.title('Distribution of the Number of Reviews')
plt.tight_layout()
plt.show()

# Visualization 3: Scatter plot for num_ratings_pages vs num_reviews
plt.figure(figsize=(10, 6))
plt.scatter(sampled_df2['num_ratings_pages'], sampled_df2['num_reviews'], color='tomato')
plt.xlabel('Number of Ratings Pages')
plt.ylabel('Number of Reviews')
plt.title('Correlation between Number of Ratings Pages and Number of Reviews')
plt.grid(True)
plt.tight_layout()
plt.show()
