import torch
import torch.nn as nn

from model.utils import get_centroids, get_cossim, calc_loss

class GE2ELoss(nn.Module):
    '''
        The loss function module itself.
        input: d-vector embeddings outputted from the network

        In general, we feed the network with log-mel filter banks associated with speaker id and utterance.
        We need to feed the network with a constant N x M matrix of filter banks of n speakers from m different utterances
        in each batch
        (we should fill up space because no one speaks exactly the same amount of time).

        (we actually have a 3D tensor of N x M x B (filter bank dimension, it would probably be 40))

        Then, we feed the matrix to a LSTM neural network and get a tensor of features (d-vectors) extracted from the network
        in size of M x N x Features.

        In order to evaluate the network, we define the Generalized end to end loss function.

        We are getting the similarity matrix between all of the embeddings from the j speaker and all of the centroids from all of the speakers
        and generate a similarity matrix which relies on the cosine similarity between 2 embeddings.

        after that the loss would be defined as

        L(e) = 1 - s(e) [j = k] + max(s(e) [j != k]).

        :math:L(e_j_i) &= -S_j_i_,_j + \log($$\sum_{k=1}^{N} e^{S_j_i_,_k})
    '''
    def __init__(self, device):
        '''
        Constructor of the network. initiates the learnable parameters w and b

        :param device: the device to use to train the network with (eg: \'cuda\', \'cpu\')
        :type device: str
        '''
        super(GE2ELoss, self).__init__()
        self.w = nn.Parameter(torch.tensor(10.0).to(device), requires_grad=True)
        self.b = nn.Parameter(torch.tensor(-5.0).to(device), requires_grad=True)
        self.device = device
        
    def forward(self, embeddings):
        '''
        This function needs to be called every forward pass through the neural network.
        It calculates the loss of the d-vector LSTM main network.

        :param embeddings: a matrix of d-vectors
        :type embeddings: torch.Tensor  
        '''
        torch.clamp(self.w, 1e-6) # clip values. Used for a protection so w wont be a 0
        centroids = get_centroids(embeddings)
        cossim = get_cossim(embeddings, centroids)
        
        sim_matrix = self.w * cossim.to(self.device) + self.b 
        loss, _ = calc_loss(sim_matrix)
        return loss