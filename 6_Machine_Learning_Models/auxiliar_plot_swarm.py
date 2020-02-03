import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
cmp = sns.set_palette('Dark2')
sns.set(context = "talk", font_scale=0.9, style = 'white', palette = cmp)

def plot_swarm_metrics(data, title, filter_regex, hue = None, hue_name = None, ylim = (0.3, 1),
                      cmap = 'Dark2', legend = True, **kwargs):
    data = data.filter(regex = filter_regex, axis = 1)
    data = data.melt(var_name='Var', value_name = 'Values')
    data['Method'] = data['Var'].apply(lambda x: x.split('-')[0])
    if hue is not None: data[hue_name] = np.tile(hue, 4)
    ax = sns.swarmplot(data = data, x = 'Method', y = 'Values', s = 5,  
                  hue = hue_name, palette = cmap, **kwargs)
    if not legend: ax.legend_.remove()
    plt.title(title)
    plt.grid(linestyle='--', linewidth='0.8')
    plt.ylim(ylim)
    
def plot_swarm_pair(df, title, col = ['DkS', 'DkLEff'], metric='ROC', **kwargs):
    plt.figure(figsize=(17,8))
    plt.subplots_adjust(wspace=0.2)
    metric = '-' + metric
    plt.subplot(1,2,1)
    plot_swarm_metrics(data = df.filter(regex=col[0], axis = 1), 
                  title = F'{title}: {col[0]} - {metric}', filter_regex = metric, **kwargs);
    plt.subplot(1,2,2)
    plot_swarm_metrics(data = df.filter(regex=col[1], axis=1), 
                  title = F'{title}: {col[1]} - {metric}', filter_regex = metric, **kwargs);