import numpy as np
import itertools
import pandas as pd
from data_pipeline.processing import ClusterInput

def class_method_validation(Class, method : str):
    if not isinstance(method, str):
        raise TypeError("Please input the method as a string.")
    elif method not in dir(Class):
        raise AttributeError(f"Error: `{method}` is not a method of {Class}.")

def multi_run(Class, data_map, params_map, method_str : str):
    if data_map.keys() != params_map.keys():
        raise ValueError("The maps `data_map` and `param_map` must have the same keys.")

    class_method_validation(Class, method_str)
    
    dict_keys = data_map.keys()

    instances = {
        data_key : Class(**params_map[data_key])
        for data_key in dict_keys
    }

    for (data_key, data) in data_map.items():
        getattr(instances[data_key], method_str)(data)

    return instances

def multi_cluster(ClusteringModel, df, feature_to_label_map, params_map, 
                  fit_method_str : str = 'fit', API = 'sklearn'):

    original_feature_names = list(df.columns)

    labels_unique = list(set(feature_to_label_map.values()))

    data_map = {
        label : ClusterInput(
            df[[col for col in df.columns if feature_to_label_map[col] == label]], API=API
            ).df 
        for label in labels_unique
        }
    
    if data_map.keys() != params_map.keys():
        raise ValueError("The maps `data_map` and `param_map` must have the same keys.")
    
    class_method_validation(ClusteringModel, fit_method_str)

    runs = multi_run(ClusteringModel, data_map, params_map, fit_method_str, fit_method_str)

    new_feat_to_label = {
        ticker : f'{old_label} {new_label}'
        for old_label in data_map.keys()
        for (ticker, new_label) in zip(data_map[old_label].index.values, runs[old_label].labels_)
        }
    
    new_feat_to_label = {
    ticker : new_feat_to_label[ticker] for ticker in original_feature_names
    }

    return {
        'labels_' : list(new_feat_to_label.values()),
        'tick_to_labels_dict' : new_feat_to_label
    }


def compute_score(ClusteringModel, data : pd.DataFrame, score_func, params, fit_method_str : str = 'fit'):
    class_method_validation(ClusteringModel, fit_method_str)
    
    model_instance = ClusteringModel(**params)

    labels = getattr(model_instance, fit_method_str)(data).labels_

    return score_func(data, labels)
    
def grid_search(ClusteringModel, data : pd.DataFrame, score_func, param_grid, fit_method_str : str = 'fit'):
    
    class_method_validation(ClusteringModel, fit_method_str)

    best_score = -np.inf
    best_params = {}

    for params in itertools.product(*param_grid.values()):
        param_dict = dict(zip(param_grid.keys(), params))
        
        score = compute_score(ClusteringModel=ClusteringModel, 
                              data=data, score_func=score_func, 
                              params=param_dict, 
                              fit_method_str=fit_method_str)

        if score > best_score:
            best_score = score
            best_params = param_dict

    return best_params

