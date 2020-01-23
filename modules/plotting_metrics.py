# Libraries
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 

class PlotMetric():
    def __init__(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred

    def plotActiveDistribution(self, colors = {1: '#e74c3c', 0: '#FCD988'}):
        order = np.argsort(y_pred)
        y_pred_ord = y_pred[order]
        y_true = y_true[order]
        colors_array = [colors[i] for i in y_true]
        sns.palplot(sns.color_palette(colors_array))
        plt.title('\n' + name + '\n', fontsize=100)
        return

    def formatMetric(self, metric, metricName):
        if not type(metricName):
            raise('Please give the name of the metric to be used.')
        
    
