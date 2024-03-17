import pandas as pd
import json
import torch

data = pd.read_csv("nlp_vectors.csv")
overview_vectors = torch.tensor([json.loads(s) for s in data['overview_vectors']])
title_vectors = torch.tensor([json.loads(s) for s in data['title_vectors']])
data = {
    "overview_vectors": overview_vectors,
    "title_vectors": title_vectors
}
torch.save(data, "nlp_vectors.pt")
