# Helper functions for 2_Docking_analysis folder
import pandas as pd
import numpy as np
from rdkit import Chem
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='white', context='talk')



def violin_plot_helper(feature, lig_datasets, xlabel='', ylabel='', title='', split=False, **kwargs):
    df_ = pd.DataFrame()
    # Create the dataset
    names_ = []
    for name, dataset in lig_datasets.items():
        a = dataset[feature]
        activity = dataset['Activity']
        n_actives = np.sum(activity == 'active')
        length = len(a)
        std_ = np.std(a).round(2)
        mean_ = np.mean(a).round(2)

        names_.append(f'{name}\nn_a/N = {n_actives}/{length}\nMean = {mean_}\nStd = {std_}')

        df_ = df_.append(
                pd.DataFrame(
                    list(zip([name]*length, a, activity)),
                    columns = ['Database', 'Feature', 'Activity']))

    plt.figure(figsize=(15,5))
    if split:
        _ = sns.violinplot(x='Database', y='Feature', hue = 'Activity',
                           data=df_, palette="Spectral", bw=.15, split=split, **kwargs)
    else:
        _ = sns.violinplot(x='Database', y='Feature', 
                           data=df_, palette="Spectral", bw=.15, **kwargs) 

    # plotting
    plt.xticks([0,1,2,3], labels=names_)
    plt.ylabel(ylabel, weight='bold')
    plt.xlabel(xlabel, weight='bold')
    plt.title(title, weight='bold')
    plt.grid(c='lightgrey')