"""
We'll have a database of movie vectors and a database of user vectors.
We'll treat users as contexts, and movies as actions. For now, we will
construct movie vectors from their vectorized data, and user vectors
as trainable parameters.
"""

class Trainer:
    def __init__(self, movie_data_file, reviews_file):
        self.reviews = pd.read_csv(reviews_file)
        pd.read_csv(movie_data_file)['movie_id']

    def train_batch(self):
        pass
