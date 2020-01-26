# Libraries
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
import pylab


# Metric imported from other libraries
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, auc

class PlotMetric:
    def __init__(self, y_true, y_pred_dict, decreasing = True, color_palette = 'Dark2', figsize = (7,7)):
        if type(y_true) is not np.ndarray:
            raise ValueError('y_true should be a numpy array with values 1 = active and 0 = inactive')
        if not np.array_equal(y_true, y_true.astype(bool)):
            assert 'y_true array must be binary'
        self.y_true = y_true
        self.N = len(y_true)
        self.n = len(y_true[y_true == 1])
        self.R_a = self.n/self.N

        if type(y_pred_dict) is not dict or len(y_pred_dict) < 1:
             raise ValueError('y_pred_dict should be a dictionary with key = "Cfl name" and value = np.array with predicted values')
        self.y_pred_dict = y_pred_dict
        if decreasing:
            for key, y_pred in y_pred_dict.items():
                self.y_pred_dict[key] = -1 * y_pred

        self.color_palette = color_palette
        self.available_metrics = {'roc_auc': self._get_roc_auc,
                                  'auac': self._get_ac_auc,
                                  'pr_auc': self._get_pr_auc,
                                  'ref_auc': self._get_ref_auc,
                                  'ef': self.get_efs}
        pylab.rcParams['figure.figsize'] = figsize
        sns.set( context = 'talk', style = 'white', palette = color_palette)
    
    # ROC
    def _get_roc(self, y_pred):
        fpr, tpr, thresholds = roc_curve(y_true = self.y_true, y_score = y_pred)
        return fpr, tpr, thresholds
    # ROC-AUC
    def _get_roc_auc(self, y_pred):
        return(roc_auc_score(y_true = self.y_true, y_score = y_pred))

    # Accumulation Curve
    def _get_ac(self, y_pred, normalized):
        N = self.N
        n = self.n
        order = np.argsort(- y_pred)
        y_true_ord = self.y_true[order]
        ranking_pos = np.linspace(0, N, N + 1)
        n_counter = 0
        f_k = np.zeros(N + 1)
        for i, k in enumerate(y_true_ord):
            if k: # If is active
                n_counter += 1
            f_k[i + 1] = n_counter
        if normalized:
            ranking_pos = ranking_pos / N
            f_k = f_k / n
        return ranking_pos, f_k

    def _get_ac_auc(self, y_pred, normalized = True):
        k, f_k = self._get_ac(y_pred = y_pred, normalized = normalized)
        auac = auc(k, f_k)
        return auac

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
    def _get_ef(self, y_pred, fractions, method):
        N = self.N
        n = self.n
        order = np.argsort(- y_pred)
        y_true_ord = self.y_true[order]
        
        efs = []
        if type(fractions) is np.ndarray:
            fractions = fractions.tolist()
        # Fractions mus be ordered
        fractions.sort()
        # Get the N_s values
        N_s_floor = [np.floor(N * f) for f in fractions]
        # If the fraction 1.0 is not in fractions we need to add it
        if fractions[-1] != 1:
            N_s_floor.append(N)
        # if 0 is given in the fractions:
        if N_s_floor[0] == 0:
            efs.append(0)
            N_s_floor.pop(0)
        # start the counting of actives at 0
        n_s = 0
        for n_mol in range(N):
            if n_mol > N_s_floor[0] and n_mol > 0:
                N_s = n_mol
                if method == 'relative':
                    ef_i = (100 * n_s) / min(N_s, n)
                elif method == 'absolute':
                    ef_i = (N * n_s) / (n * N_s)
                elif method == 'normalized':
                    ef_i = n_s / min(N_s, n)
                efs.append(ef_i)
                N_s_floor.pop(0)
            active = y_true_ord[n_mol]
            if active:
                n_s += 1
        if fractions[-1] == 1 and N_s_floor[0] == N:
            if method == 'relative': 
                ef_i = 100
            else: 
                ef_i = 1
            efs.append(ef_i)
        return efs
    
    def get_efs(self, method, fractions = [0.005, 0.01, 0.02, 0.05], rounded = 2):
        ef_results = {}
        for key, y_pred in self.y_pred_dict.items():
            ef_results[key] = self._get_ef(y_pred, method = method, fractions = fractions)
        names = {'relative': 'REF', 'absolute': 'EF', 'normalized': 'NEF'}
        row_names_ef = [F'{names[method]} at {i*100}%' for i in fractions]
        df_efs = pd.DataFrame(ef_results, index = row_names_ef)
        df_efs["#ligs at X%"] = [np.floor(i* self.N) for i in fractions]
        df_efs = df_efs.round(rounded)
        return df_efs

    def _get_ref_auc(self, y_pred, method, max_chi = 1):
        fractions = np.linspace(0.0, max_chi, len(self.y_true) - 2 )
        efs = self._get_ef(y_pred = y_pred, method = method, fractions = fractions)
        efs_auc = auc(fractions, efs)
        return efs_auc

    def _add_plot_ef(self, y_pred, label, max_chi, max_num_of_ligands, method = 'normalized',  **kwargs):
        fractions = np.linspace(0.0, 1, len(self.y_true) - 2 )
        names = {'relative': 'REF', 'absolute': 'EF', 'normalized': 'NEF'}
        efs = self._get_ef(y_pred = y_pred, method = method, fractions = fractions)
        # Calculate max # of ranked values to show
        if max_num_of_ligands is not None and max_chi == 1:
            n_rankers = max_num_of_ligands
            fractions = range(n_rankers)
            efs = efs[:n_rankers]
        else:
            n_rankers = int(np.ceil(max_chi*len(fractions)))
            fractions = fractions[:n_rankers]
            efs =  efs[:n_rankers]
        efs_auc = auc(fractions, efs)
        if method == 'absolute':
            label = label + F' {names[method]}'
        else:
            label = label + F' {names[method]}-AUC' + ' = %0.2f' % efs_auc
        plt.plot(fractions, efs, label = label, **kwargs)

    def plot_ef_auc(self, title, method = 'normalized', 
                    max_chi = 1, max_num_of_ligands = None,
                    keys_to_omit = [], key_to_plot = None, key_to_fade = None,
                     fontsize='x-small', showplot = True, show_by_itself=True, **kwargs):

        methods = ('relative', 'absolute', 'normalized')
        method = method.lower()
        if method not in methods:
            raise AttributeError(F'method value, {method} is not available.\nAvailable methods are:\n{methods}')
        sns.color_palette(self.color_palette)

        if method == 'absolute' and max_num_of_ligands is not None:
            raise AttributeError(F'arguments method="absolute" and "max_num_of_ligands" can not be applied together.')
        for key, y_pred in self.y_pred_dict.items():
            if key in keys_to_omit:
                continue
            if key_to_fade == key:
                self._add_plot_ef(y_pred, method = method, label = key, 
                        max_chi = max_chi, max_num_of_ligands = max_num_of_ligands,
                        linestyle = '--', 
                        linewidth = 1.5, **kwargs)
                continue
            if type(key_to_plot) is str and key_to_plot in self.y_pred_dict.keys():
                key = key_to_plot
                y_pred = self.y_pred_dict[key]
                self._add_plot_ef(y_pred, method = method, label = key, 
                                    max_chi = max_chi, max_num_of_ligands = max_num_of_ligands, **kwargs)
                break
            self._add_plot_ef(y_pred, method = method, label = key, 
                                    max_chi = max_chi, max_num_of_ligands = max_num_of_ligands, **kwargs)
        if showplot:
            plt.legend(fontsize=fontsize)
            if method == 'absolute':
                plt.plot([self.R_a, self.R_a], [0 , 1/self.R_a], 'k--', c = 'grey')
                plt.plot([0, 1], [1, 1], 'k--', c = 'grey')
            if max_num_of_ligands is not None and max_chi == 1:
                plt.xlabel("# ligands at ranking top")
            else:
                plt.xlabel("Ranking Fraction")
            plt.ylabel("Enrichment Factor")
            #plt.ylim(0, 1.1)
            plt.grid(linestyle='--', linewidth='0.8')
            plt.title(title)
            if show_by_itself:
                plt.show()

    def _add_plot_pr(self, y_pred, label, **kwargs):
        precision, recall, thresholds = self._get_pr(y_pred)
        auc_pr = self._get_pr_auc(y_pred)
        plt.plot(recall, precision, label = label + ' AUC-PR = %0.2f' % auc_pr, **kwargs)

    def plot_pr_auc(self, title, keys_to_omit = [], key_to_plot = None, key_to_fade = None,
                     fontsize='x-small', showplot = True, show_by_itself=True, **kwargs):
        sns.color_palette(self.color_palette)
        
        for key, y_pred in self.y_pred_dict.items():
            if key in keys_to_omit:
                continue
            if key_to_fade == key:
                self._add_plot_pr(y_pred, label = key, linestyle = '--', 
                        linewidth = 1.5, **kwargs)
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
            if show_by_itself:
                plt.show()

    # Plotting functions
    def _add_plot_roc(self, y_pred, label, **kwargs):
        fpr, tpr, thresholds = self._get_roc(y_pred)
        auc = self._get_roc_auc(y_pred)
        plt.plot(fpr, tpr, label = label + ' AUC-ROC = %0.2f' % auc, **kwargs)
        
    def plot_roc_auc(self, title, keys_to_omit = [], key_to_plot = None, key_to_fade = None,
                     fontsize='small', showplot = True, show_by_itself=True, **kwargs):
        sns.color_palette(self.color_palette)
        
        for key, y_pred in self.y_pred_dict.items():
            if key in keys_to_omit:
                continue
            if key_to_fade == key:
                self._add_plot_roc(y_pred, label = key, linestyle = '--', 
                        linewidth = 1.5, **kwargs)
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
            if show_by_itself:
                plt.show()

    def _add_plot_ac(self, y_pred, label, normalized = True, **kwargs):
        k, f_k = self._get_ac(y_pred = y_pred, normalized = normalized)
        auc_ac = self._get_ac_auc(y_pred = y_pred, normalized = normalized)
        plt.plot(k, f_k , label = label + ' AUAC = %0.2f' % auc_ac, **kwargs)

    def plot_auac(self, title, keys_to_omit = [], key_to_plot = None, key_to_fade = None, normalized = True,
                     fontsize='small', showplot = True, show_by_itself=True, **kwargs):
        sns.color_palette(self.color_palette)
        
        for key, y_pred in self.y_pred_dict.items():
            if key in keys_to_omit:
                continue
            if key_to_fade == key:
                self._add_plot_ac(y_pred, label = key, normalized = normalized,
                linestyle = '--', linewidth = 1.5, **kwargs)
                continue
            if type(key_to_plot) is str and key_to_plot in self.y_pred_dict.keys():
                key = key_to_plot
                y_pred = self.y_pred_dict[key]
                self._add_plot_ac(y_pred, label = key, normalized = normalized, **kwargs)
                break
            self._add_plot_ac(y_pred, label = key, normalized = normalized, **kwargs)
        if showplot:
            plt.legend(fontsize=fontsize)
            if normalized:
                x_label = 'Normalized ranking positions (x = k/N)'
                y_label = 'Normalized num. of actives (Fa(x))'
            else:
                x_label = 'Ranking positions (k)'
                y_label = 'Num. of actives (Fa(k))'
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.grid(linestyle='--', linewidth='0.8')
            plt.title(title)
            if show_by_itself:
                plt.show()
        
    # Plotting distributions
    def plot_actives_distribution(self, colors = {1: '#e74c3c', 0: '#FCD988'}):
        for key, y_pred in self.y_pred_dict.items():
            order = np.argsort(-y_pred)
            y_pred_ord = y_pred[order]
            y_true = self.y_true[order]
            colors_array = [colors[i] for i in y_true]
            sns.palplot(sns.color_palette(colors_array))
            plt.title('\n' + key + '\n', fontsize=100)

    # Formating metrics
    def format_metric_results(self, metric_name='roc_auc', 
                              rounded = 3, transposed = True, *kwargs):
        if metric_name not in self.available_metrics:
            raise ValueError(F'Metric {metric_name} is not available. ' + 
                  F'Available metrics are:\n{self.available_metrics.keys()}')
        metric = self.available_metrics[metric_name]
        dic_results = {}
        for key, y_pred in self.y_pred_dict.items():
            dic_results[key] = metric(y_pred, *kwargs)
        df = pd.DataFrame(dic_results, index = [metric_name.upper().replace('_', ' ')])
        df = df.T if transposed else df
        return df.round(rounded)
    
#def plot_grid(list_of_plots, metric_to_plot, )