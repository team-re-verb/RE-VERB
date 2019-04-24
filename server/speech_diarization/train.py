"""
code snippets and structure insipration taken from HarryVolek on GitHub
"""
import os
import random
import time
import h5py
import torch
from torch.utils.data import DataLoader

from hparam import hparam as hp
from data_load import SpeakerDatasetTIMIT, SpeakerDatasetTIMITPreprocessed
from speech_embedder_net import SpeechEmbedder, GE2ELoss, get_centroids, get_cossim
from loader import AMI_Dataset

def train(model_path):
    # set device to train on (CPU or GPU)
    device = torch.device(hp.device)

    # dataset loader(fetches a batch)
    train_dataset = AMI_Dataset()
    train_loader = DataLoader(train_dataset, shuffle=True, num_workers=hp.train.num_workers, drop_last=True) 

    embedder_net = SpeechEmbedder().to(device)
    
    if hp.train.restore:
        embedder_net.load_state_dict(torch.load(model_path))
    ge2e_loss = GE2ELoss(device)
    
    #Both net and loss have trainable parameters
    optimizer = torch.optim.SGD([
                    {'params': embedder_net.parameters()},
                    {'params': ge2e_loss.parameters()}
                ], lr=hp.train.lr)
    
    os.makedirs(hp.train.checkpoint_dir, exist_ok=True)
    
    embedder_net.train()
    iteration = 0

    for e in range(hp.train.epochs):
        total_loss = 0
        for batch_id, batch in enumerate(train_loader): 
            batch = batch.to(device)
            embeddings = torch.zeros([batch.shape[0], batch.shape[1] ,hp.model.proj]) #(num_speakers, num_utter,num_features)

            for speaker_id,speaker in enumerate(batch):
                for utter_id, utterance in enumerate(speaker):
                    embeddings[speaker_id,utter_id] = embedder_net(utterance)                

            #gradient accumulates

            optimizer.zero_grad()
            
            #get loss, call backward, step optimizer
            loss = ge2e_loss(embeddings) #wants (Speaker, Utterances, embedding)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(embedder_net.parameters(), 3.0)
            torch.nn.utils.clip_grad_norm_(ge2e_loss.parameters(), 1.0)
            optimizer.step()
            
            total_loss = total_loss + loss
            iteration += 1
            if (batch_id + 1) % hp.train.log_interval == 0:
                mesg = "{0}\tEpoch:{1}[{2}/{3}],Iteration:{4}\tLoss:{5:.4f}\tTLoss:{6:.4f}\t\n".format(time.ctime(), e+1,
                        batch_id+1, len(train_dataset)//hp.train.N, iteration,loss, total_loss / (batch_id + 1))
                print(mesg)
                if hp.train.log_file is not None:
                    with open(hp.train.log_file,'a') as f:
                        f.write(mesg)
                    
        if hp.train.checkpoint_dir is not None and (e + 1) % hp.train.checkpoint_interval == 0:
            embedder_net.eval().cpu()
            ckpt_model_filename = "ckpt_epoch_" + str(e+1) + "_batch_id_" + str(batch_id+1) + ".pth"
            ckpt_model_path = os.path.join(hp.train.checkpoint_dir, ckpt_model_filename)
            torch.save(embedder_net.state_dict(), ckpt_model_path)
            embedder_net.to(device).train()

    #save model
    embedder_net.eval().cpu()
    save_model_filename = "final_epoch_" + str(e + 1) + "_batch_id_" + str(batch_id + 1) + ".model"
    save_model_path = os.path.join(hp.train.checkpoint_dir, save_model_filename)
    torch.save(embedder_net.state_dict(), save_model_path)
    
    print("\nDone, trained model saved at", save_model_path)

def test(model_path):
    pass
    # TODO: calc DER
        
if __name__=="__main__":
    if hp.training:
        train(hp.model.model_path)
    else:
        test(hp.model.model_path)