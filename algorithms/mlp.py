"""
Use a general function approximator to approximate the Q-function.

There is some interesting recent work by Google DeepMind called
"Stop Regressing!" - they reframe the traditional thought of a regression
problem into a classification problem. We will consider this later though.
"""

import torch
from torch.distributions import Normal

# Creates a standard normal distribution.
normal = Normal(torch.tensor(0), torch.tensor(1))

class MLP(torch.nn.Module):
    def __init__(self, input_dims, hidden_dims, output_dims):
        super(MLP, self).__init__()
        self.fc1 = torch.nn.Linear(input_dims, hidden_dims)
        self.fc2 = torch.nn.Linear(hidden_dims, output_dims)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def create_hl_gaussian_target(rewards: torch.Tensor, v_min: float, v_max: float, m: int, hl_gaussian_sigma_over_binsize: float):
    """
    Implementation of the Histogram Loss Gaussian (HL-Gauss) method used in
    [https://arxiv.org/abs/2403.03950](Stop Regressing: Training Value Functions via Classification for Scalable Deep RL),
    a paper released by DeepMind.

    TLDR: Call this function with the true rewards, and a set of bins to discretize them into,
    and it will return a categorial probability distribution.

    The method for reformulating regression as classification is to
    convert continuous rewards to different logprobs in discrete buckets.

    There are a couple methods for this:
     * Two-shot: Interpolating between the nearest buckets.
     * HL-Gauss: Distributing reward over bins via Gaussian.

    For HL-Gauss, we calculate the correct probability mass to assign to each bin
    via a Gaussian integral. At each index, we assume that it is responsible for
    the range [index - 0.5, index + 0.5]. For index 0 and index m-1, we include
    -infty and +infty to make the probability distribution sum to 1.

    The mean of the Gaussian integral is the reward value.

    
    :params:
     - `rewards`: a tensor of rewards. Shape: [batch]
     - `v_min`: the minimum value of the reward distribution.
     - `v_max`: the maximum value of the reward distribution.
     - `m`: the number of bins to create.
     - `hl_gaussian_sigma_over_binsize`: a hyperparameter. Useful to tune the approx. number of bins a reward Gaussian will
        distribute to. 0.75 is a value used in the original paper.
        See Page 6 for more info.

    :returns:
     - `probs`: a tensor representing the probability mass assigned to each bin, for each reward value specified. Shape: [batch, m]

    """

    bin_size = (v_max - v_min) / m
    bin_centers = torch.arange(m).float() * bin_size + v_min + bin_size / 2
    bin_left_boundaries = bin_centers - bin_size / 2
    bin_right_boundaries = bin_centers + bin_size / 2
    sigma = hl_gaussian_sigma_over_binsize * bin_size

    # Transform bin_left_boundaries to z-scores.
    # [batch, m]
    rewards_ = rewards.unsqueeze(-1)
    left_z_scores = (bin_left_boundaries.unsqueeze(0).repeat(rewards.shape[0], 1) - rewards_) / sigma
    right_z_scores = (bin_right_boundaries.unsqueeze(0).repeat(rewards.shape[0], 1) - rewards_) / sigma
    upper_integrals = normal.cdf(right_z_scores)
    lower_integrals = normal.cdf(left_z_scores)
    lower_integrals[:, 0] = 0
    upper_integrals[:, -1] = 1

    # Integrate.
    probs = upper_integrals - lower_integrals

    # For debugging. Disable when actually training.
    __DEBUG__ = False

    if __DEBUG__:
        prob_sum = torch.sum(probs, dim=1)
        assert torch.max((prob_sum - 1.0).abs()) < 1e-8, f"Probabilities did not sum to 1 within tolerance level."

        # expected_values = torch.sum(probs * bin_centers, dim=1)
        # assert torch.max((expected_values - rewards).abs()) < 1e-8, f"Expected values did not match rewards within tolerance level."
        # There will be some slight loss here, because we clip the Gaussian tail that goes below v_max or above v_min.

    return probs

if __name__ == '__main__':
    rewards = torch.tensor([1, 2, 3, 4])
    create_hl_gaussian_target(rewards, v_min=0, v_max=10, m=10, hl_gaussian_sigma_over_binsize=0.75)
