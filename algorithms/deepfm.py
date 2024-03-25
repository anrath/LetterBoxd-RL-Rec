import torch
import torch.nn as nn

"""
Short DeepFM implementation
"""

class DeepFM(nn.Module):
    def __init__(self, movie_vector_size: int, user_vector_size: int, num_dense_movie_embeddings: int, num_dense_user_embeddings: int, dense_embedding_size: int, mlp_sizes: list):
        super().__init__()
        
        self.movie_dense_embeddings = nn.Linear(movie_vector_size, dense_embedding_size * num_dense_movie_embeddings + 1)
        self.user_dense_embeddings = nn.Linear(user_vector_size, dense_embedding_size * num_dense_user_embeddings + 1)
        self.dense_embedding_size = dense_embedding_size

        assert mlp_sizes[-1] == 1
        mlp_input_size = (num_dense_movie_embeddings + num_dense_user_embeddings) * dense_embedding_size
        mlp_layers = []
        for i in range(len(mlp_sizes)):
            mlp_layers.append(nn.Linear(mlp_input_size, mlp_sizes[i]))
            if i != len(mlp_sizes) - 1:
                mlp_layers.append(nn.ReLU())
            mlp_input_size = mlp_sizes[i]

        self.mlp = nn.Sequential(*mlp_layers)

    def forward(self, movie_vectors, user_vectors):
        batch_size = movie_vectors.shape[0]
        movie_dense = self.movie_dense_embeddings(movie_vectors)
        user_dense = self.user_dense_embeddings(user_vectors)

        # calculate factorization machine hidden states
        fm_additive = movie_dense[..., -1] + user_dense[..., -1]
        movie_dense_split = movie_dense[..., :-1].view(batch_size, -1, self.dense_embedding_size)
        user_dense_split = user_dense[..., :-1].view(batch_size, -1, self.dense_embedding_size)
        fm_interactions = torch.einsum('bik,bjk->bij', movie_dense_split, user_dense_split).view(batch_size, -1)

        all_dense = torch.cat([movie_dense[..., :-1], user_dense[..., :-1]], dim=-1)

        logit = self.mlp(all_dense) + fm_additive.unsqueeze(-1) + fm_interactions.sum(dim=-1, keepdim=True)

        return logit

