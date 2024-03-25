import torch
import torch.nn as nn
import pandas as pd

from movie_metadata_table import MovieMetadataTable

import sys
sys.path.append("../algorithms")
from deepfm import DeepFM # type: ignore

def train_loop(train_user_ids=None, train_movie_ids=None):
    ratings = pd.read_csv("../data/ratings_export.csv")

    if train_user_ids is not None:
        ratings = ratings[ratings['user_id'].isin(train_user_ids)]

    if train_movie_ids is not None:
        ratings = ratings[ratings['movie_id'].isin(train_movie_ids)]

    # iterate over ratings in random batches
    indexes = torch.randperm(len(ratings))
    batch_size = 16

    user_ids = ratings['user_id'].unique()
    movie_ids = ratings['movie_id'].unique()

    user_vector_size = 64
    user_id_to_index = {user_id: i for i, user_id in enumerate(user_ids)}
    user_embedding_table = nn.Embedding(len(user_ids), user_vector_size)
    movie_metadata_table = MovieMetadataTable(
        movie_ids_file="../data/movie_ids.json",
        movie_data_vectorized_file="../data/vectorizing/movie_data_vectorized.csv",
        nlp_vectors_file="../data/vectorizing/nlp_vectors.csv",
    )
    deepfm = DeepFM(
        movie_metadata_table.movie_vector_size,
        user_vector_size,
        num_dense_movie_embeddings=8,
        num_dense_user_embeddings=4,
        dense_embedding_size=16,
        mlp_sizes=[16, 16, 1],
    )

    for batch_start in range(0, len(indexes), batch_size):
        batch = ratings.iloc[indexes[batch_start:batch_start + batch_size]]

        movie_ids = batch['movie_id'].values
        train_user_ids = batch['user_id'].values
        ratings = batch['rating_val'].values

        print(movie_ids)

        print(train_user_ids)

        print(ratings)

        break

train_loop()
