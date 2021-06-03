import torch
import torch.nn as nn
import torch.nn.functional as F
from treys import Card


class CardEmbeddings(nn.Module):
    def __init__(self, dim):
        super(CardEmbeddings, self).__init__()
        self.rank = nn.Embedding(13, dim)
        self.suit = nn.Embedding(4, dim)
        self.card = nn.Embedding(52, dim)

    def forward(self, input):
        n, num_cards = input.shape
        x = input.view(-1)

        embs = self.card(x) + self.rank(map(Card.get_rank_int, x)) \
               + self.suit(map(Card.get_suit_int, x))

        return embs.view(n, num_cards, -1).sum(axis=1)

