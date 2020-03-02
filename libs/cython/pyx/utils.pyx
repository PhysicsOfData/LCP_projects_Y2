#!python
#distutils: language=c++
#cython: language_level=3, boundscheck=False

# use cython extension of numpy
import numpy as np
cimport numpy as np

ctypedef (int, double) edge_weight_t

# Method to convert the edgelist back to a dense matrix (Just for debugging purposes)
def list2matrix(list edgelist, weighted=True):
    cdef int N = len(edgelist)
    cdef np.ndarray A_mat
    if weighted:
        A_mat = np.zeros([N,N], dtype=np.float64)
    else:
        A_mat = np.zeros([N,N], dtype=np.int)
    cdef int i = 0
    cdef list node
    cdef edge_weight_t neighbour_weight
    cdef int neighbour
    for i, node in enumerate(edgelist):
        if weighted:
            for neighbour_weight in node:
                A_mat[i, neighbour_weight[0]] = neighbour_weight[1]
        else:
            for neighbour in node:
                A_mat[i, neighbour] = 1
    return A_mat

def getDegree(list edges):
    cdef edge_weight_t e
    if len(edges) == 0:
        return 0
    else:
        degree = 0
        for e in edges:
            degree += e[1]
        return degree

def getInOutDegree(list edgelist):
    cdef int N = len(edgelist)
    cdef np.ndarray outDegs = np.zeros([N], dtype=np.float64)
    cdef np.ndarray inDegs = np.zeros([N], dtype=np.float64)
    cdef double out_deg = 0.
    cdef int i = 0
    cdef list n
    cdef edge_weight_t edge

    # for each node and list
    for i, n in enumerate(edgelist):
        # initialize out degree
        out_deg = 0.
        # for each weight
        for edge in n:
            # update out degree
            out_deg += edge[1]
            # and in degree
            inDegs[edge[0]] += edge[1]
        # set out degree to the correct value
        outDegs[i] = out_deg

    return list(inDegs), list(outDegs)

# compute the transposition of the edgelist
def transposeEdgelist(list edgelist, weighted=False):
    cdef int N = len(edgelist)
    cdef list edgelist_t = [[]]*N
    cdef int i
    cdef list nodelist
    cdef (int, double) edge_weighted
    cdef int edge

    for i in range(len(edgelist_t)):
        edgelist_t[i] = []

    if weighted:
        for i, nodelist in enumerate(edgelist):
            for edge_weighted in nodelist:
                edgelist_t[edge_weighted[0]].append((i, edge_weighted[1]))
    else:
        for i, nodelist in enumerate(edgelist):
            for edge in nodelist:
                edgelist_t[edge].append(i)

    return edgelist_t
