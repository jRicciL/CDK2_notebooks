import pandas as pd
import numpy as np
import glob
import os
import sys
import pickle
sys.path.append('..')

# ML models from sklearn
from sklearn.svm import SVC


def get_mds_subspaces(file_name, path = ''):
    with open(path + file_name, 'rb') as f:
        mds_ = pickle.load(f)
    return mds_




# main
if __name__ == "__main__":

