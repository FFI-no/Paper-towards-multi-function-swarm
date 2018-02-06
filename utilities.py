import pickle
import os

def open_pickle(filename):
	if filename is None or not os.path.exists(filename):
		return None

	f = open(filename,"r")
	data = pickle.load(f)
	f.close()

	return data