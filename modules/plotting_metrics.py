# Libraries
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
# Metric imported from other libraries
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, auc

class PlotMetric:
    def __init__(self, y_true, y_pred_dict, decreasing = False, color_palette = 'Paired'):
        if type(y_true) is not np.ndarray:
            raise ValueError('y_true should be a numpy array with values 1 = active and 0 = inactive')
        self.y_true = y_true
        self.N = len(y_true)
        self.n = len(y_true[y_true == 1])
        self.R_a = n/N

        if type(y_pred_dict) is not dict or len(y_pred_dict) < 1:
             raise ValueError('y_pred_dict should be a dictionary with key = "Cfl name" and value = np.array with predicted values')
        self.y_pred_dict = y_pred_dict
        if decreasing:
            for key, y_pred in y_pred_dict.items():
                y_pred_dict[key] = -1 * y_pred

        self.color_palette = color_palette
        self.available_metrics = {'roc_auc': self._get_roc_auc,
                                        'pr_auc': self._get_pr_auc}
    
    # ROC
    def _get_roc(self, y_pred):
        fpr, tpr, thresholds = roc_curve(y_true = self.y_true, y_score = y_pred)
        return fpr, tpr, thresholds
    # ROC-AUC
    def _get_roc_auc(self, y_pred):
        return(roc_auc_score(y_true = self.y_true, y_score = y_pred))

    # Precision and Recall
    def _get_pr(self, y_pred):
        precision, recall, thresholds = precision_recall_curve(y_true = self.y_true, probas_pred = y_pred)
        return precision, recall, thresholds
    # PR-AUC
    def _get_pr_auc(self, y_pred):
        precision, recall, thresholds = self._get_pr(y_pred = y_pred)
        pr_auc = auc(recall, precision)
        return pr_auc

    # Enrichment Factor
    def _get_ef(y_true, y_pred, fractions = [0.005, 0.01, 0.02, 0.05], 
                   decreasing = True, relative = False):
    N = len(y_true)
    n = sum(y_true == 1)
    if decreasing:
        order = np.argsort(y_pred)
    else:
        order = np.argsort(- y_pred)
    y_pred_ord = y_pred[order]
    y_true_ord = y_true[order]
    
    efs = []
    N_s_floor = [np.floor(N * f) for f in fractions]
    n_s = 0
    for n_mol in range(N):
        if n_mol > (N_s_floor[0]) and n_mol > 0:
            N_s = n_mol
            if relative: ef_i = (100 * n_s) / min(N_s, n)
            else: ef_i = (N * n_s) / (n * N_s)
            efs.append(ef_i)
            N_s_floor.pop(0)
        active = y_true_ord[n_mol]
        if active:
            n_s += 1
    # Checks if
    if N_s_floor and N_s_floor[0] == N:
        if relative: 
            ef_i = (100 * n) / n
            efs.append(ef_i)
        else: efs.append(1.0)
    return efs

def get_ref_auc(y_true, y_pred):
    if not np.array_equal(y_true, y_true.astype(bool)):
        assert 'y_true array must be binary'
    fractions = np.linspace(0.0, 1, len(y_true) - 2 )
    efs = get_EF(y_true = y_true, y_pred = y_pred, 
                 fractions = fractions, relative = True)
    efs_auc = auc(fractions, efs)
    return efs_auc

    def _add_plot_pr(self, y_pred, label, **kwargs):
        precision, recall, thresholds = self._get_pr(y_pred)
        auc = self._get_pr_auc(y_pred)
        plt.plot(recall, precision, label = label + ' AUC-PR = %0.2f' % auc, **kwargs)

    def plot_pr_auc(self, title, keys_to_omit = [], key_to_plot = None,
                     fontsize='x-small', showplot = True, **kwargs):
        sns.color_palette(self.color_palette)
        
        for key, y_pred in self.y_pred_dict.items():
            if key in keys_to_omit:
                continue
            if type(key_to_plot) is str and key_to_plot in self.y_pred_dict.keys():
                key = key_to_plot
                y_pred = self.y_pred_dict[key]
                self._add_plot_pr(y_pred, label = key, **kwargs)
                break
            self._add_plot_pr(y_pred, label = key, **kwargs)
        if showplot:
            plt.legend(fontsize=fontsize)
            no_skill = self.R_a
            plt.plot([0, 1], [no_skill, no_skill], 'k--')
            plt.xlabel("Recall")
            plt.ylabel("Precision")
            plt.ylim(0, 1.1)
            plt.grid(linestyle='--', linewidth='0.8')
            plt.title(title)
            plt.show()

    # Plotting functions
    def _add_plot_roc(self, y_pred, label, **kwargs):
        fpr, tpr, thresholds = self._get_roc(y_pred)
        auc = self._get_roc_auc(y_pred)
        plt.plot(fpr, tpr, label = label + ' AUC-ROC = %0.2f' % auc, **kwargs)
        
    def plot_roc_auc(self, title, keys_to_omit = [], key_to_plot = None,
                     fontsize='small', showplot = True, **kwargs):
        sns.color_palette(self.color_palette)
        
        for key, y_pred in self.y_pred_dict.items():
            if key in keys_to_omit:
                continue
            if type(key_to_plot) is str and key_to_plot in self.y_pred_dict.keys():
                key = key_to_plot
                y_pred = self.y_pred_dict[key]
                self._add_plot_roc(y_pred, label = key, **kwargs)
                break
            self._add_plot_roc(y_pred, label = key, **kwargs)
        if showplot:
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

    # Formating metrics
    def format_metric_results(self, metric_name='roc_auc', 
                              rounded = 3, transposed = True):
        if metric_name not in self.available_metrics:
            raise ValueError(F'Metric {metric_name} is not available. ' + 
                  F'Available metrics are:\n{self.available_metrics.keys()}')
        metric = self.available_metrics[metric_name]
        dic_results = {}
        for key, y_pred in self.y_pred_dict.items():
            dic_results[key] = metric(y_pred)
        df = pd.DataFrame(dic_results, index = [metric_name.upper().replace('_', ' ')])
        df = df.T if transposed else df
        return df.round(rounded)
    
    