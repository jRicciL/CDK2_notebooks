# Libraries
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
# Metric imported from other libraries
from sklearn.metrics import roc_curve, roc_auc_score

class PlotMetric:
    def __init__(self, y_true, y_pred_dict, decreasing = False, color_palette = 'Paired'):
        if type(y_true) is not np.ndarray:
            raise('y_true should be a numpy array with values 1 = active and 0 = inactive')
        self.y_true = y_true

        if type(y_pred_dict) is not dict or len(y_pred_dict) < 1:
             raise('y_pred_dict should be a dictionary with key = "Cfl name" and value = np.array with predicted values')
        self.y_pred_dict = y_pred_dict
        if decreasing:
            for key, y_pred in y_pred_dict.items():
                y_pred_dict[key] = -1 * y_pred

        self.color_palette = color_palette
    
    # ROC
    def _get_roc(self, y_pred):
        fpr, tpr, thresholds = roc_curve(y_true = self.y_true, y_score = y_pred)
        return fpr, tpr, thresholds
    # ROC-AUC
    def _get_roc_auc(self, y_pred):
        return(roc_auc_score(y_true = self.y_true, y_score = y_pred))

    def _add_plot_roc(self, y_pred, label, **kwargs):
        print(kwargs.items())
        fpr, tpr, thresholds = self._get_roc(y_pred)
        auc = self._get_roc_auc(y_pred)
        plt.plot(fpr, tpr, label = label + ' AUC = %0.2f' % auc, **kwargs)
        

    def plot_roc_auc(self, title, keys_to_omit = [], fontsize='small', lw = 3, linestyle = '-'):
        sns.color_palette(self.color_palette)
        for key, y_pred in self.y_pred_dict.items():
            if key in keys_to_omit:
                continue
            self._add_plot_roc(y_pred, label = key, lw = lw, linestyle = '-')
        plt.legend(fontsize=fontsize)
        plt.plot([0, 1], [0, 1], 'k--', c = 'gray')
        plt.xlabel("FPR (1 - specificity)")
        plt.ylabel("TPR (sensitivity)")
        plt.grid(linestyle='--', linewidth='0.8')
        plt.title(title)
        plt.show()
        
    # Plotting distributions
    def plot_actives_distribution(self, colors = {1: '#e74c3c', 0: '#FCD988'}):
        for key, y_pred in self.y_pred_dict.items():
            order = np.argsort(y_pred)
            y_pred_ord = y_pred[order]
            y_true = self.y_true[order]
            colors_array = [colors[i] for i in y_true]
            sns.palplot(sns.color_palette(colors_array))
            plt.title('\n' + key + '\n', fontsize=100)
    
    

class PlotMetric():
    def __init__(self, EvalClf):
        if type(EvalClf) is dict:
            self.cfl_dictionary = EvalMetric

    def plotActiveDistribution(self, colors = {1: '#e74c3c', 0: '#FCD988'}):
        order = np.argsort(y_pred)
        y_pred_ord = y_pred[order]
        y_true = y_true[order]
        colors_array = [colors[i] for i in y_true]
        sns.palplot(sns.color_palette(colors_array))
        plt.title('\n' + name + '\n', fontsize=100)
        return

    def formatMetric(self, metric, metricName):
        if type(metricName) is not str:
            raise('Please give the name of the metric to be used.')
        
    def plot_roc_auc(self):
        inverted_input = np.negative(predicted_values)
        fpr, tpr, thresholds = roc_curve(true_values, inverted_input)
        auc = roc_auc_score( y_true = true_values, y_score = inverted_input)
        plt.plot(fpr, tpr, label= label + ' AUC = %0.2f' % auc, lw = 3, linestyle = linestyle)
        
    
