# first line: 1
@memory.cache
def n_hold_out_validation(
          estimators, X, y,
          metrics,
          n_reps=5, test_size=0.25,
          random_state=None, **kwargs):
    # Compute the Stratified K folds
    cv = StratifiedShuffleSplit(
                        n_splits=n_reps, 
                        test_size=test_size,
                        random_state=random_state)
    splits = [*cv.split(X, y)]
    
    results = _do_replicates(splits, estimators, X, y,
          metrics, **kwargs)
    
    df_res = _format_results_to_df(metrics, results, n=n_reps)
    
    return df_res 
