import json
from sklearn.model_selection import train_test_split
import os

# Define the path to the JSON file
json_file_path = 'data/movie_ids.json'

# Read the JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Split the data into training and test sets
train_data, test_data = train_test_split(data, test_size=0.1, random_state=42)

# Save the training set to a new JSON file
train_file_path = 'data/movie_train_data.json'
with open(train_file_path, 'w') as file:
    json.dump(train_data, file)

# Save the test set to a new JSON file
test_file_path = 'data/movie_test_data.json'
with open(test_file_path, 'w') as file:
    json.dump(test_data, file)

print("Training data shape:", len(train_data))
print("Test data shape:", len(test_data))