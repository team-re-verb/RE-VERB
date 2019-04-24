import torch
from torch.utils.data import Dataset

import numpy as np
import h5py
from hparam import hparam as hp

class AMI_Dataset(Dataset):
    def __init__(self):
        self.meetings = h5py.file(hp.data.dataset_path)
        self.keys = sorted(list(self.meetings.keys()), key=lambda k: int(k))
        
        offset = int(self.size * len(self.keys))


        # dataset is a dict of meetings each containing (speakers, utterances, embeddings)
        if hp.training:
            self.size = hp.data.train_size
            self.speaker_num = hp.train.N
            self.utter_num = hp.train.M

            self.keys = self.keys[: offset]
        
        else: # testing
            self.size = 1 - hp.data.train_size
            self.speaker_num = hp.test.N
            self.utter_num = hp.test.M

            self.keys = self.keys[offset :]

        if self.shuffle:
            random.shuffle(self.keys)  # shuffle meetings

    def __del__(self):
        self.meetings.close()
        super(Dataset,self).__del__()

    def __len__(self):
        count = 0

        for i in self.keys:
            count += (meeting[i].shape[1] / self.utter_num)

        return count

    def __getitem__(self, idx):
        # fetches one batch
        for i in self.keys:
            table_rows = int(self.meetings[i].shape[1] / self.utter_num)
            
            if idx >= table_rows:
                idx -= (table_rows + 1)
            else:
                return torch.from_numpy(self.meetings[i][:, idx * self.utter_num: idx* (self.utter_num + 1)]).float()