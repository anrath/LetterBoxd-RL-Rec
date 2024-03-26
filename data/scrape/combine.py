import pandas as pd
import os
import json
from tqdm import tqdm

def process_json_files(directory):
    """
    Process JSON files in the specified directory, adding their contents to a pandas DataFrame.
    Each item in the JSON file is added as a row, and a 'user' column is added to denote the source file,
    with the file name (without the '.json' extension) as the value. A tqdm progress bar is displayed.

    Args:
    - directory (str): The path to the directory containing JSON files.

    Returns:
    - pandas.DataFrame: A DataFrame containing the data from the JSON files, with an additional 'user' column.
    """
    frames = []  # List to store individual dataframes created from each JSON file
    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    
    for filename in tqdm(files, desc="Processing JSON files"):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            data = json.load(file)
            temp_df = pd.DataFrame(data)
            temp_df['user'] = filename[:-5]  # Add column with the file name (excluding '.json')
            frames.append(temp_df)

    # Concatenate all dataframes in the list to a single dataframe
    combined_df = pd.concat(frames, ignore_index=True)

    return combined_df

# Directory containing the JSON files
temp_directory = '/root/projects/school/LetterBoxd-RL-Rec/runs/review'

# Process the JSON files and save the resulting DataFrame to a CSV file
df = process_json_files(temp_directory)
df = df[['date', 'film_slug', 'user', 'rating', 'review']]
csv_file_path = 'user_reviews.tsv'
df.to_csv(csv_file_path, sep='\t', index=False)
