import torch
from torch.distributions import MultivariateNormal

"""
LinCB is an interesting potential algorithm.
It requires finding a matrix inverse for an NxN matrix, though, where N is the number of features.
If our embedding matrices are too large, we will need to reduce their dimensionality.
Fortunately, it seems like the text embedding vectors have 384 dimensions, which isn't too large.
"""

# potential evaluation method: regression error
class LinCB:
    def __init__(self, vector_dims: int, use_sherman_morrison_inverse = False):
        self.vector_dims = vector_dims
        self.lambda_matrix = torch.eye(vector_dims)
        self.lambda_matrix_inv = torch.eye(vector_dims)
        # cumulative sum of phi_i * r_i for i = 1 ... t - 1
        self.phir_sum = torch.zeros(vector_dims)
        self.use_sherman_morrison_inverse = use_sherman_morrison_inverse
        self.policy = torch.zeros(vector_dims) # placeholder. Requires at least one example to calibrate.

    def update(self, context, reward):
        """
        Context shape must be [batch, vector dims].
        We can update with a whole batch at a time if we want.
        """
        # [vector_dims, batch] @ [batch, vector_dims] => [vector_dims, vector_dims], which is the correct shape.
        # Reasoning is that context is a set of *row* vectors, and to compute the outer product for several column vectors
        outer_product = context.T @ context
        self.lambda_matrix += outer_product
        self.phir_sum += reward * context
        # We can theoretically make this inverse calculation faster by using the Sherman-Morrison formula.
        if self.use_sherman_morrison_inverse:
            # Update the matrix one-by-one
            for i in range(len(context)):
                u = context[i].unsqueeze(1)
                self.lambda_matrix_inv -= (self.lambda_matrix_inv @ (u @ u.T) @ self.lambda_matrix_inv) / (1 + u.T @ self.lambda_matrix_inv @ u)
        else:
            self.lambda_matrix_inv = torch.inverse(self.lambda_matrix)
        # Ensure symmetry (because of floating point errors)
        self.lambda_matrix_inv = (self.lambda_matrix_inv + self.lambda_matrix_inv.T) / 2
        # make sure!!!! that it is symmetric
        self.policy = self.lambda_matrix_inv @ self.phir_sum

    def __call__(self, context, use_thompson_sampling=False):
        if not use_thompson_sampling:
            # [batch, vector_dims] @ [vector_dims] => [batch]
            return context @ self.policy
        
        distrib = MultivariateNormal(loc=self.policy, covariance_matrix=self.lambda_matrix_inv)
        policy_with_exploration = distrib.rsample()
        
        return context @ policy_with_exploration
