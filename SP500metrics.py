import numpy as np
import pandas as pd

def WCSS(prices, clusters):
    distances_to_center = []
    labels = list(set(clusters.values()))
    for label in labels:
        ticks_in_cluster = [tick for tick in clusters.keys() if clusters[tick] == label]
        cluster = prices[ticks_in_cluster]
        cluster_centered = cluster.sub(cluster.mean(axis = 1), axis=0)
        sum_dists_to_center = np.linalg.norm(cluster_centered)**2
        distances_to_center.append(sum_dists_to_center)
    return sum(distances_to_center)
