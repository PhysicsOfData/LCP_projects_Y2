import numpy as np
from matplotlib import pyplot as plt
import heapq as hq
import networkx as nx
import pandas as pd

def cluster1(L_norm, centroids, A_mat=None, pos=None, colors=None, node_size=10, draw_edges=False):
    # initialize queue with the centroids
    # queue element: (weight, (centroid, path_length))
    queue = [(-1., centroid) for centroid in centroids]
    # initialize the clusters vector
    clusters = -np.ones(len(L), dtype=int)
    clusters[centroids] = centroids
    iters = 0
    
    # iterate until the queue is not empty
    while len(queue)>0:
        
        # pop the first element
        elem = hq.heappop(queue)
        node = elem[1]
        
        #print("Current Weight:", elem[0])
        
        # extract the neighbours
        neighs = L[node]
        
        # for each neighbour
        for neigh in neighs:
            # if it wasn't already assigned
            if clusters[neigh[0]] == -1:
                # assign it to the parent's cluster
                clusters[neigh[0]] = clusters[node]
                # and push it into the global list
                if neigh[1] > 0:
                    hq.heappush(queue, ( elem[0]*neigh[1], neigh[0] ))
                else:
                    hq.heappush(queue, ( elem[0]/2, neigh[0] ))
                
        #if iters%75 == 0:
        #    if A_mat is not None:
        #        pos, colors = plotNetworkClusters(A_mat, list(clusters), node_size, draw_edges=draw_edges, pos=pos, colors=colors)
                
        iters += 1

    if A_mat is not None:
        plotNetworkClusters(A_mat, list(clusters), node_size, draw_edges=draw_edges, pos=pos, colors=colors)
    return clusters

def cluster2(L_norm, centroids, A_mat=None, pos=None, colors=None, node_size=10, draw_edges=False):
    # initialize queue with the centroids
    # queue element: (weight, (node, parent's cluster))
    queue = [(-1., (centroid, centroid)) for centroid in centroids]
    # initialize the clusters vector
    clusters = -np.ones(len(L), dtype=int)
    iters = 0
    
    # iterate until the queue is not empty
    while len(queue)>0:
        
        # pop the first element
        elem = hq.heappop(queue)
        node = elem[1][0]
        clust = elem[1][1]
        
        # if the node was not already assigned
        if clusters[node] == -1:
            
            #assign it to the parent's cluster
            clusters[node] = clust
        
            # extract the neighbours
            neighs = L[node]

            # for each neighbour
            for neigh in neighs:
                # if it wasn't already assigned
                if clusters[neigh[0]] == -1:
                    # and push it into the global list
                    if neigh[1] > 0:
                        hq.heappush(queue, ( elem[0]*neigh[1], (neigh[0], clust) ))
                    else:
                        hq.heappush(queue, ( elem[0]/len(neighs), (neigh[0], clust) ))
                
        #if iters%75 == 0:
        #    if A_mat is not None:
        #        pos, colors = plotNetworkClusters(A_mat, list(clusters), node_size, draw_edges=draw_edges, pos=pos, colors=colors)
                
        iters += 1

    if A_mat is not None:
        plotNetworkClusters(A_mat, list(clusters), node_size, draw_edges=draw_edges, pos=pos, colors=colors)
    return clusters