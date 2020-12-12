import numpy as np

def get_three_ranking_cases(true_values, sufix = '', include_optimal = False):
    '''Returns a dictionary of three ranking cases. Each value of the dictionary is 
    a numpy array of N scores which value depends on the case it belongs.
    '''
    if type(true_values) is not np.ndarray:
        raise ValueError('y_true should be a numpy array with values 1 = active and 0 = inactive')
    if not np.array_equal(true_values, true_values.astype(bool)):
        assert 'y_true array must be binary'

    n = len(true_values[true_values == 1])
    N = len(true_values)

    case_1 = np.zeros(N)
    n_actives = 0
    for i, active in enumerate(true_values):
        if active:
            n_actives += 1
            case_1[i] = -3 if n_actives <= n/2 else -1
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
    inverse = (1/np.floor(N/n))
    for i, active in enumerate(true_values):
        if active:
            n_activos += 1
            case_3[i] = n_activos
            continue
        if n_negativos%np.floor(N/n) == 0:
            case_3[i] = n_counter + inverse/2
            n_counter += 1 + inverse
        else:
            case_3[i] = n_counter - inverse/2
        n_negativos += 1
        
    cases_dic = {F'{sufix}Case 1': case_1,
                 F'{sufix}Case 2': case_2,
                 F'{sufix}Case 3': case_3}

    if include_optimal:
        optimal = true_values*(-10)
        cases_dic[F'{sufix}Perfect']= np.array(optimal)

    return cases_dic