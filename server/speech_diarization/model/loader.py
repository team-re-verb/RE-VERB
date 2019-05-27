import torch
from torch.utils.data import Dataset
import random
import numpy as np
import h5py
from model.hparam import hp

class AMI_Dataset(Dataset):
    '''
    This class is used to load and split the dataset in order to create batches (in parallel).  
    (It inherits the torch.utils.data.Dataset class).

    In practice, the instance of this class is used with the DataLoader class. 
    (this class only specifies how to parse the dataset)
    '''


    def __init__(self, shuffle=False):
        '''
        The constructor this class

        :param shuffle: whether to pick utterances randomally
        :type shuffle: bool 
        '''
        self.meetings = h5py.File(hp.data.dataset_path, 'r')
        self.keys = sorted(list(self.meetings.keys()), key=lambda k: int(k))
        
        offset = int(hp.data.train_size * len(self.keys))


        # dataset is a dict of meetings each containing (speakers, utterances, embeddings)
        if hp.training:
            self.size = hp.data.train_size
            #self.speaker_num = hp.train.N
            self.utter_num = hp.train.M

            self.keys = self.keys[: offset]
        
        else: # testing
            self.size = 1 - hp.data.train_size
            #self.speaker_num = hp.test.N
            self.utter_num = hp.test.M

            self.keys = self.keys[offset :]

        if shuffle:
            random.shuffle(self.keys)  # shuffle meetings

    def __del__(self):
        '''
        The destructor of the class. We need to close the dataset
        in order to not block it from use later
        '''
        self.meetings.close()
        #super.__del__()

    def __len__(self):
        '''
        Python special function which tells the length of an object.
        In this class, this function is used in order to get the number of batches available
        '''
        count = 0

        for i in self.keys:
            count += (self.meetings[i].shape[1] // self.utter_num)

        return count

    def __getitem__(self, idx):
        '''
        Python special function which gets a specific index from an object. eg: obj[1] will call the __getitem__(1) function
        In this class, this function is used in order to get a specific batch
        '''
        # fetches one batch
        for i in self.keys:
            table_rows = int(self.meetings[i].shape[1] / self.utter_num)
            
            if idx >= table_rows:
                idx -= (table_rows + 1)
            else:
                return torch.from_numpy(self.meetings[i][:, idx * self.utter_num: (idx * self.utter_num) + self.utter_num,:]).float()