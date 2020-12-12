# first line: 1
@memory.cache
def k_cross_validation(
          estimators, X, y,
          metrics,
          n_splits=5, 
          random_state=None, 
          shuffle=True):
    # Compute the Stratified K folds
    cv = StratifiedKFold(n_splits=n_splits, 
                         random_state=random_state,
                         shuffle=shuffle)
    splits = [*cv.split(X, y)]
    
    results = _do_replicates(splits, estimators, X, y, 
                             metrics)
    
    df_res = _format_results_to_df(metrics, results, n=n_splits)
    
    return df_res 
