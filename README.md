# CS 6501: Reinforcement Learning, Class Project
## Reel Recommendations
Leverage Reinforcement Learning and Language Models to perform movie recommendations for LetterBoxd users.

We use offline reinforcement learning and language modeling to provide movie recommendations based on user data from LetterBoxd, popular movie review and cataloging website, and movie data from TMDB. We implement DeepFM, a framework for converting sparse features to dense embeddings. Additionally, we formulate the recommendation task as a language modeling task by fine-tuning GPT-2 to predict movie ratings based on a sequence of previously rated movies. For implementation details see [Reel Recommendations Report](Reel_Recommendations_Report.pdf)!

![sample graph](/data/figures/scatter_weighted.png)