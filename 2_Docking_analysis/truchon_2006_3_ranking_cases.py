import numpy as np

def get_three_ranking_cases(true_values):
    '''Returns a dictionary of three ranking cases. Each value of the dictionary is 
    a numpy array of N scores which value depends on the case it belongs.
    '''
    n = len(true_values[true_values == 1])
    N = len(true_values)
    
    case_1 = np.zeros(N)
    for i, active in enumerate(true_values):
        if active:
            case_1[i] = -3 if i <= n/2 else -1
        else:
            case_1[i] = -2
            
    case_2 = np.zeros(N)
    n_negativos = 0
    for i, active in enumerate(true_values):
        if active:
            case_2[i] = -2
            continue
        n_negativos += 1
        if n_negativos <= (N - n)/2:
            case_2[i] = -3
        else:
            case_2[i] = -1
            
    case_3 = np.zeros(N)
    n_negativos, n_counter = 0, 0
    n_activos = 0
    for i, active in enumerate(true_values):
        if active:
            n_activos += 1
            case_3[i] = n_activos
            continue
        if n_negativos%np.floor(N/n) == 0:
            case_3[i] = n_counter + 0.1
            n_counter += 1.25
        else:
            case_3[i] = n_counter + 0.1
        n_negativos += 1
        
    cases_dic = {'case_1': case_1,
                 'case_2': case_2,
                 'case_3': case_3}
    return cases_dic