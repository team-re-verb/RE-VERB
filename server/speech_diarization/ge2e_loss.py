import numpy as np
from numpy import linalg as LA
from sklearn.metrics.pairwise import cosine_similarity

from math import e

N = 3 #Number of speakers
M = 5 #Utterances of speakers

def get_centroid(mat):
    c = []
    length = mat.shape[0]

    for i in range(mat.shape[1]):
        c.append(np.sum(mat[:, i]) / length)

    return np.array(c)



def get_similarity_matrix(centroids, embeddings):
    sim_mat = np.zeros(centroids.shape[1], embeddings.shape[0] / M)

    for j,k in (embeddings, centroids):
        cos_sim = w * cosine_similarity(embeddings[:, j], centroids[:, k]) + b
        sim_mat[j,k] = cos_sim

    return sim_mat


def sigmoid(x):
    return 1 / (1 + e ** -x)







def GE2E(j_embs, k_embs, j, k):
    '''
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


        WHAT I DONT KNOW YET: 
            - how to get k and j while training

            - how to train the network with assigned embedings (Eji, Ck) instead with the vanilla form of x_train and y_train
              (we need to clarify what is x and what is y for our network seince every fb has a speaker id (filter-bank, n) 
              and we train the net according to both x and y)
              
            - how to implement the custom loss in keras

            - we have different number of speakers in each batch, and not M 
    '''

    centroids = np.array([get_centroid(k_embs[:,i]) for i in k_embs.shape[1]])
    sim_mat = get_similarity_matrix(centroids, j_embs)

    return (
        1 - 
        np.sum([sigmoid(i) for i in np.diagonal(sim_mat)]) + 
        np.max([sigmoid(i) if cond else 0 for (i,cond) in (sim_mat, np.where(~np.eye(sim_mat.shape[0],dtype=bool)))])
    )



def TE2E(emb, mat, w, b, j, k):
    sigma = lambda x,y: 1 if x == y else 0

    centroid = get_centroid(mat)
    sim = w * cosine_similarity(centroid,emb) + b

    return sigma(j,k)* sigmoid(sim) + (1 - sigma(j,k))*(1 - sigmoid(sim))