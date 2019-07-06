import torch
import torch.nn as nn

from model.hparam import hp

class SpeechEmbedder(nn.Module):
    '''
    This class is used as the class for the main LSTM d-vector embedding network as described in Quan Wang's paper (https://arxiv.org/abs/1710.10468).
    This class inherits from torch.nn.Module and represets a neural network.
    '''
    
    def __init__(self):
        '''
        The constructor of this class.
        It initiates a few things:
         
        - LSTM layers according to configuration in config/config.yaml
        - Initiates the weights and biases
        - Regular feed forward layer
        '''
        super(SpeechEmbedder, self).__init__()    
        self.LSTM_stack = nn.LSTM(input_size=hp.data.nfilters, hidden_size=hp.model.hidden, num_layers=hp.model.num_layer) #batch_first=True
        for name, param in self.LSTM_stack.named_parameters():
          if 'bias' in name:
             nn.init.constant_(param, 0.0)
          elif 'weight' in name:
             nn.init.xavier_normal_(param)
        self.projection = nn.Linear(hp.model.hidden, hp.model.proj)
        
    def forward(self, x):
        '''
        This function needs to be called every forward pass through the neural network.
        It calculates the embeddings from the logmel filterbanks inputs.

        :param x: a matrix of N x M (number of speakers, utteraces)
        :type x: torch.Tensor
        '''
        x, _ = self.LSTM_stack(x.float()) #(batch, frames, n_mels)
        #only use last frame
        x = x[:,x.size(1)-1]
        x = self.projection(x.float())
        x = x/torch.norm(x)
        return x