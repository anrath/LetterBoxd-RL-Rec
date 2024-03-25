"""
We'll have a database of movie vectors and a database of user vectors.
We'll treat users as contexts, and movies as actions. For now, we will
construct movie vectors from their vectorized data, and user vectors
as trainable parameters.
"""

import pandas as pd
import torch

def vectorize_string_array(string):
    return [int(x) for x in string[1:-1].split(" ")]

class MovieEmbeddingTable:
    def __init__(self, movie_metadata_file, nlp_vectors_file):
        self.movie_metadata = pd.read_csv(movie_metadata_file)

        """
        convert to tensor:
        - popularity [scalar]
        - runtime [scalar]
        - vote_average [scalar]
        - vote_count [scalar; log1p transform]
        - year_released [scalar; converted to one-hot indicator of decade]
        - // release_date_ordinal [scalar]
        - genres_encoded [one-hot]
        - production_countries_encoded [one-hot]
        - spoken_languages_encoded [one-hot]
        """
        
        # shape: [270422, 32]
        df = self.movie_metadata
        genres_vectorized = df['genres_encoded'].map(vectorize_string_array)
        countries_vectorized = df['production_countries_encoded'].map(vectorize_string_array)
        lang_vectorized = df['spoken_languages_encoded'].map(vectorize_string_array)
        
        self.movie_tensor = torch.cat([
            torch.tensor(df['popularity']).unsqueeze(-1),
            torch.tensor(df['runtime']).unsqueeze(-1),
            torch.tensor(df['vote_average']).unsqueeze(-1),
            torch.tensor(df['vote_count']).unsqueeze(-1).log1p(),
            torch.tensor(genres_vectorized),
            torch.tensor(countries_vectorized),
            torch.tensor(lang_vectorized),
        ], dim=-1)
        nlp_vectors = torch.load(nlp_vectors_file)
        self.overview_vectors = nlp_vectors['overview_vectors']
        self.title_vectors = nlp_vectors['title_vectors']

    def __call__(self, movie_id):
        return torch.cat([
            self.movie_tensor[movie_id],
            self.overview_vectors[movie_id],
            self.title_vectors[movie_id],
        ], dim=-1)

class Trainer:
    def __init__(self):
        pass

    def train_batch(self):
        pass
