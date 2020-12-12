# first line: 1
@memory.cache
def _do_replicates(splits, 
                   estimators, X, y,
                   metrics):
    results={}
    # Machine Learning Classifiers
    for clf_name, clf in estimators.items():
        folds = []
        for i, (train, test) in enumerate(splits):
            if clf_name.startswith('ml_'):
                # Fit the ml classifier once per fold
                cfl = _train_cfl(clf, X[train], y[train])
            
            # for each metric
#             metric_results = {}
            for metric_name, metric_params in metrics.items():
            
                metric = _validate(
                    clf, clf_name, 
                    X[test], y[test],
                    metric_name, metric_params
                )
                # Append the results
                folds.append(metric)

        # Add to the results dictonary 
        results[clf_name] = folds

    return results
