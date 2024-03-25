import pandas as pd
import json
import torch

def vectorize_string_array(string):
    return [int(x) for x in string[1:-1].split(" ")]

class MovieMetadataTable:
    def __init__(self, movie_ids_file, movie_data_vectorized_file, nlp_vectors_file):
        with open(movie_ids_file, 'r') as f:
            self.movie_ids = json.load(f)
        self.movie_id_to_index = {movie_id: i for i, movie_id in enumerate(self.movie_ids)}
        self.movie_metadata = pd.read_csv(movie_data_vectorized_file)

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

        self.movie_vector_size = (
            self.movie_tensor.shape[-1] +
            self.overview_vectors.shape[-1] +
            self.title_vectors.shape[-1]
        )

    def __call__(self, movie_index):
        if type(movie_index) == str:
            movie_index = self.movie_id_to_index[movie_index]
        elif type(movie_index) == list:
            movie_index = [self.movie_id_to_index[movie_id] for movie_id in movie_index]

        return torch.cat([
            self.movie_tensor[movie_index],
            self.overview_vectors[movie_index],
            self.title_vectors[movie_index],
        ], dim=-1)