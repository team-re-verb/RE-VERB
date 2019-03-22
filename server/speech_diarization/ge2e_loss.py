import numpy as np


def get_similarity_matrix():


def get_centroid(mat):
	length = mat.shape[0]
	sums = []

	for i in range(mat.shape[1]):
		sums.append(np.sum(mat[:, i]) / length)
		
	return np.array(sums)


def GE2E_loss(y_pred, Y_test):
    centroid = get_centroid(Y_test)
    



    return None
