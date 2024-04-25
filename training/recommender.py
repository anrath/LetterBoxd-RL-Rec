import torch
import torch.nn as nn
import torch.nn.functional as F
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

    all_user_ids = ratings['user_id'].unique()
    all_movie_slugs = ratings['movie_id'].unique()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    user_vector_size = 64
    user_id_to_index = {user_id: i for i, user_id in enumerate(all_user_ids)}
    user_embedding_table = nn.Embedding(len(all_user_ids), user_vector_size).to(device)
    movie_metadata_table = MovieMetadataTable(
        movie_ids_file="../data/movie_ids.json",
        movie_data_vectorized_file="../data/vectorizing/movie_data_vectorized.csv",
        nlp_vectors_file="../data/vectorizing/nlp_vectors.pt",
    )
    deepfm = DeepFM(
        movie_metadata_table.movie_vector_size,
        user_vector_size,
        num_dense_movie_embeddings=8,
        num_dense_user_embeddings=4,
        dense_embedding_size=16,
        mlp_sizes=[16, 16, 1],
    ).to(device)
    deepfm.apply(add_dropout)

    # note: if we want to get a massive speedup,
    # we can probably use a sparse optimization scheme somehow
    optim = torch.optim.Adam([
        *deepfm.parameters(),
        *user_embedding_table.parameters()
    ], lr=0.001, weight_decay=1e-5)  # L2 regularization

    # determine how to give a reward
    # we will just give a reward if the user rated the movie >= 7/10

    loss_type = "mse"

    for batch_start in range(0, len(indexes), batch_size):
        batch = ratings.iloc[indexes[batch_start:batch_start + batch_size]]

        movie_slugs = [str(x) for x in batch['movie_id'].values]
        train_user_ids = batch['user_id'].values
        ratings = batch['rating_val'].values

        user_indices = torch.tensor([user_id_to_index[user_id] for user_id in train_user_ids], device=device)
        user_vectors = user_embedding_table(user_indices)
        movie_vectors = movie_metadata_table(movie_slugs).to(device)

        predictions = deepfm(movie_vectors.float(), user_vectors.float()).squeeze(-1)
        rewards = torch.tensor(ratings >= 7, device=device)

        if loss_type == 'mse':
            # resembles learning q function
            loss = F.mse_loss(predictions, rewards)
        elif loss_type == 'binary_crossentropy':
            # loosely resembles policy gradient
            loss = F.binary_cross_entropy_with_logits(predictions, rewards.float())

        optim.zero_grad()
        loss.backward()
        optim.step()

        print(loss.item())

def add_dropout(module):
    if isinstance(module, nn.Linear):
        module.dropout = nn.Dropout(p=0.5)

train_loop()
