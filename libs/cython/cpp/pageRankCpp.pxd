#!python
#distutils: language=c++
#cython: language_level=3

from libcpp.utility cimport pair
from libcpp.vector cimport vector
from libcpp cimport bool as cbool

cdef extern from "page_rank.cpp":
    pass

cdef extern from "page_rank.h":
    ctypedef pair[int, double] edge_weight_t
    ctypedef vector[edge_weight_t] nodelist_weight_t
    ctypedef vector[nodelist_weight_t] edgelist_weight_t
    ctypedef vector[int] nodelist_t
    ctypedef vector[nodelist_t] edgelist_t
    ctypedef pair[vector[double], vector[double]] double_vec_pair_t

    double getDegree(nodelist_weight_t edges)
    edgelist_weight_t localPageRank_weight(edgelist_weight_t A, double c, double epsilon, int max_iter, cbool return_only_neighbours)
    edgelist_weight_t localPageRank(edgelist_t A, double c, double epsilon, int max_iter, cbool return_only_neighbours)
    double_vec_pair_t approximateSimrank(edgelist_t A, int v, double alpha, double epsilon, int max_iters, cbool return_only_neighbours)
