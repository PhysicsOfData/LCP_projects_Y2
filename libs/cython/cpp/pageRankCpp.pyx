#!python
#distutils: language=c++
#cython: language_level=3

from pageRankCpp cimport getDegree, localPageRank_weight, localPageRank, approximateSimrank

def cppGetDegree(edges):
  return getDegree(edges)

def cppLocalPageRank_weight(A, c, epsilon=1e-5, max_iters=200, return_only_neighbours=False):
  return localPageRank_weight(A, c, epsilon, max_iters, return_only_neighbours)

def cppLocalPageRank(A, c, epsilon=1e-5, max_iters=200, return_only_neighbours=False):
  return localPageRank(A, c, epsilon, max_iters, return_only_neighbours)

def cppApproximateSimrank(A, v, alpha, epsilon=1e-5, max_iters=200, return_only_neighbours=False):
  return approximateSimrank(A, v, alpha, epsilon, max_iters, return_only_neighbours)
