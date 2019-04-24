import torch
import torch.nn as nn

from utils import get_centroids, get_cossim, calc_loss

class GE2ELoss(nn.Module):
    '''
        The loss function module itself.
        input: d-vector embeddings outputted from the network

        In general, we feed the network with log-mel filter banks associated with speaker id and utterance.
        We need to feed the network with a constant N x M matrix of filter banks of n speakers from m different utterances
        in each batch
        (we should fill up space because no one speakes exactly the same amount of time).

        (we actually have a 3D tensor of N x M x B (filter bank dimension, it would probably be 40))

        Then, we feed the matrix to a LSTM neural network and get a tensor of featues (d-vectors) extracted from the network
        in size of M x N x Featues.

        In order to evaluate the network, we define the Generelized end to end loss function.

        We are getting the similarity matrix between all of the embedings from the j speaker and all of the centroids from all of the speakers
        and generate a similarity matrix which relies on the cosine similarity between 2 embeddings.

        after that the loss would be defined as

        L(e) = 1 - s(e) [j = k] + max(s(e) [j != k]).
    '''
    def __init__(self, device):
        super(GE2ELoss, self).__init__()
        self.w = nn.Parameter(torch.tensor(10.0).to(device), requires_grad=True)
        self.b = nn.Parameter(torch.tensor(-5.0).to(device), requires_grad=True)
        self.device = device
        
    def forward(self, embeddings):
        torch.clamp(self.w, 1e-6) # clip values
        centroids = get_centroids(embeddings)
        cossim = get_cossim(embeddings, centroids)
        # w and b are learnable parameters and get optimised with the SGD
        sim_matrix = self.w * cossim.to(self.device) + self.b 
        loss, _ = calc_loss(sim_matrix)
        return loss