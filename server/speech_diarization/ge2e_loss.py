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

    centroids = [get_centroid(k_embs[:,i]) for i in k_embs.shape[1]]
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