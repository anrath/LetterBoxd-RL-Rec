import pandas as pd
from sklearn.model_selection import train_test_split

# Read the CSV file
data = pd.read_csv('data/users_export.csv')

# Split the data into training and test sets based on the 'username' column
user_train_data, user_test_data = train_test_split(data, test_size=0.1, random_state=42)

# Save the training set to the data folder as JSON
user_train_data.to_json('data/user_training_set.json', orient='records')

# Save the test set to the data folder as JSON
user_test_data.to_json('data/user_test_set.json', orient='records')

# Print the shapes of the training and test sets
print("Training set shape:", user_train_data.shape)
print("Test set shape:", user_test_data.shape)
