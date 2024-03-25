import torch
import torch.nn as nn

# stores vectors in memory.
# could likely be updated to lazily allocate embedding table space.
class UserVectorTable(nn.Module):
    def __init__(self, capacity: int, num_dimensions: int):
        self.embedding = nn.Parameter(torch.randn(capacity, num_dimensions))
        pass
