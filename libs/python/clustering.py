import numpy as np
import pandas as pd
import networkx as nx
import heapq as hq

def generate_edges(positions, radius=1, weighted=False):
    # initialize the edgelist
    N = positions.shape[0]
    idxs = np.arange(N)
    A = [[]]*N

    # generate the edgelist
    for i in range(N):
        point = positions[i,:]
        dists = np.linalg.norm(point-positions, axis=1)
        neighs = idxs[np.logical_and(dists<=radius, idxs!=i)]
        A[i] = []
        for j, neigh in enumerate(neighs):
            if weighted:
                A[i].append((neigh, 1 + 1./dists[idxs!=i][j]))
            else:
                A[i].append(neigh)

    # return the generated edgelist
    return A

def build_network(path, sep='\t', radius=1, weighted=False):
    df = pd.read_csv(path, sep=sep, names=["x", "y", "cluster"])
    clusters = np.array(df.cluster)
    positions = np.array(df[["x", "y"]])
    A = generate_edges(positions, radius, weighted)
    return A, positions, clusters

def cluster1(L_norm, centroids, alpha):
    # initialize the output vector with the clusters
    clusters = - np.ones(len(L_norm))

    # initialize the heap queues related to the clusters
    queues = []

    # insert centroids in the queues, e.g. (expansions, (node, rank))
    for i in range(centroids.size):
        queue = []
        hq.heappush(queue, (0, (centroids[i], 1)))
        queues.append(queue)

        # set the centroid cluster
        clusters[centroids[i]] = centroids[i]

    # iterate until all the nodes are assigned to the clusters
    exit_ext = False
    while not exit_ext:
        cumulative_length = 0
        for queue in queues:
            # assign the new expansions
            for i, node in enumerate(queue):
                # ensure at least one expansion per node
                expansions = max(1, np.round(alpha*node[1][1])) # TODO: eventually change the round function

                # modify the queue element with the new expansions
                queue[i] = (
                    - expansions,
                    (node[1][0], node[1][1])
                )

            # restore the queue
            hq.heapify(queue)

            # expand the cluster boundary toward the high ranked nodes
            exit_int = False
            while (not exit_int) and len(queue)>0:
                # pop a node that should be expanded
                node = hq.heappop(queue)

                # check the termination condition
                expansions_opp = node[0]
                if expansions_opp==0:
                    # no more nodes to expand
                    exit_int = True
                else:
                    # reduce the remained number of expansions
                    expansions_opp += 1

                    # expand the neighbourhood and assign the new expansions
                    for edge in L_norm[node[1][0]]:
                        #print(neighbour)
                        neighbour = edge[0]
                        # assign the node to the cluster
                        if clusters[neighbour]<0:
                            #print("assigned")
                            clusters[neighbour] = clusters[node[1][0]]

                            # add the node to the queue
                            rank = edge[1]
                            hq.heappush(
                                queue,
                                (
                                    np.round(expansions_opp*rank),
                                    (neighbour, rank)
                                )
                            )
            cumulative_length += len(queue)
        exit_ext = cumulative_length==0

    # return the vector with the clusters
    return clusters

def cluster2(L_norm, centroids):
    # initialize queue with the centroids
    # queue element: (weight, (centroid, path_length))
    queue = [(-1., centroid) for centroid in centroids]

    # initialize the clusters vector
    clusters = -np.ones(len(L_norm), dtype=int)
    clusters[centroids] = centroids
    iters = 0

    # iterate until the queue is not empty
    while len(queue)>0:

        # pop the first element
        elem = hq.heappop(queue)
        node = elem[1]

        # extract the neighbours
        neighs = L_norm[node]

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

        iters += 1

    # return the vector with the clusters
    return clusters

def cluster3(L):
    clusters = -np.ones(len(L), dtype=int)
    parents = np.zeros(len(L), dtype=int)

    # for each node and its neighbours
    for idx in range(len(L)):
        # if it was not already assigned to a cluster:
        if clusters[idx] == -1:
            clusters[idx] = idx
            exit_flag = False
            curr_node = idx
            if len(L[curr_node]) == 0:
                exit_flag = True
            while not exit_flag:
                next_node = max(L[curr_node], key=lambda x:x[1])[0]
                if clusters[next_node] == -1:
                    clusters[next_node] = idx
                    parents[next_node] = curr_node
                    curr_node = next_node
                else:
                    # if the path didn't close on itself
                    if not clusters[next_node] == idx:
                        # walk backwards and reassign the nodes to the correct cluster
                        while curr_node != idx:
                            clusters[curr_node] = clusters[next_node]
                            curr_node = parents[curr_node]
                        clusters[idx] = clusters[next_node]
                    exit_flag = True

    # return the clusters
    return clusters

# A and L are expected in edgelist form, measure is a numpy array
def cluster4(L_T):

    def getNeighsAvgDegree(node_list, degree):
        out = 0.
        for node in node_list:
            out += degree[node[0]]
        if len(node_list) > 0:
            return out/len(node_list)
        else:
            return 0

    def cluster_std(nodes, measure):
        clust_measure = measure[nodes]
        if clust_measure.shape[0] <= 1:
            return 0.
        return 1/(clust_measure.std())

    # compute the average neighbours inDegree
    # precompute the inDegree of each node
    inDeg = [0.]*len(L_T)
    for n, node_list in enumerate(L_T):
        for _, w in node_list:
            inDeg[n] += w
    # compute the actual average, also equal to measure
    avgNeighsInDeg = [0.]*len(L_T)
    for i, node_list in enumerate(L_T):
        avgNeighsInDeg[i] = getNeighsAvgDegree(node_list, inDeg)

    measure = np.array(avgNeighsInDeg)
    order = np.argsort(measure)
    #order = np.arange(len(L_T))

    # node id 0->N-1
    clusters = np.arange(len(L_T), dtype=int)
    idxs = np.arange(len(L_T), dtype=int)
    link_to_follow = [[True for _ in node_list] for node_list in L_T]

    # initialize exit flag
    flag=True
    # while the exit flag is not False do
    while flag:
        flag = False
        old_clusts = np.array(clusters)
        # for each node
        for n, c in enumerate(clusters[order]):
            # extract the current cluster
            n = order[n]
            curr_cluster = idxs[clusters==c]
            # follow the link that corresponds to it's maximum relevance
            weights = np.array([e[1] for e in L_T[n]])[link_to_follow[n]]
            if weights.shape[0] > 0:
                max_idx = np.argmax(weights)
                link_to_follow[n][max_idx] = False
                neigh = L_T[n][max_idx][0]
                # make sure that the nodes are in different clusters
                if c != clusters[neigh]:
                    neigh_cluster = idxs[clusters==clusters[neigh]]
                    merge = cluster_std(list(curr_cluster)+list(neigh_cluster), measure)
                    clust1 = cluster_std(list(curr_cluster), measure)
                    clust2 = cluster_std(list(neigh_cluster), measure)
                    if clust1==clust2==0:
                        split = 0
                    else:
                        #split = 2*clust1*clust2/(clust1**2+clust2**2)
                        size_ratio = (curr_cluster.shape[0]*neigh_cluster.shape[0])/(curr_cluster.shape[0]+neigh_cluster.shape[0])
                        split = 2*size_ratio*clust1*clust2/(clust1**2+clust2**2)
                    #print("node:", n, "merge:", merge, "split", split)
                    if merge > split:
                        clusters[neigh_cluster] = c


        flag = not np.all(clusters==old_clusts)

    return clusters
