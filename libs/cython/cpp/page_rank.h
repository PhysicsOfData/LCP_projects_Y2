#ifndef CPP_PAGERANK_H
#define CPP_PAGERANK_H

#include <vector>
#include <utility>

// queue element, needed to extend the comparison
class queue_elem_t{
  public:
     int node;
     double weight;

     queue_elem_t(int node, double weight);

     bool operator>(const queue_elem_t& rhs) const;
     bool operator>=(const queue_elem_t& rhs) const;
     bool operator<(const queue_elem_t& rhs) const;
     bool operator<=(const queue_elem_t& rhs) const;
     bool operator==(const queue_elem_t& rhs) const;
     bool operator!=(const queue_elem_t& rhs) const;
};

// declare types
// general
typedef std::vector<double> double_vec_t;
typedef std::vector<bool> bool_vec_t;
typedef std::pair<double_vec_t, double_vec_t> double_vec_pair_t;
// unweighted list
typedef std::vector<int> nodelist_t;
typedef std::vector<nodelist_t> edgelist_t;
// weighted
typedef std::pair<int, double> edge_weight_t;
typedef std::vector<edge_weight_t> nodelist_weight_t;
typedef std::vector<nodelist_weight_t> edgelist_weight_t;


// unweighted netweorks implementation
bool_vec_t push(double_vec_t &p, double_vec_t &r,
                double alpha, int u, double du, nodelist_t &neighbours,
                                  double_vec_t &neighbours_deg, double epsilon);
// c-only implementation of the approximateSimrank
double_vec_pair_t approximateSimrank(edgelist_t &A, int v, double alpha,
            double epsilon, int max_iters=200, bool return_only_neighbours=false);
// c-only implementation of the localPageRank
edgelist_weight_t localPageRank(edgelist_t &A, double c, double epsilon=1e-5,
                            int max_iters=200, bool return_only_neighbours=false);
// weighted networks implementations
// c-only implementation of getDegree
double getDegree(nodelist_weight_t edges);
// c-only implementation of the push operation
bool_vec_t push_weight(double_vec_t &p, double_vec_t &r,
                double alpha, int u, double du, nodelist_weight_t &neighbours,
                                  double_vec_t &neighbours_deg, double epsilon);
// c-only implementation of the approximateSimrank
double_vec_pair_t approximateSimrank_weight(edgelist_weight_t &A, double_vec_t &degs, int v, double alpha,
            double epsilon, int max_iters=200, bool return_only_neighbours=false);
// c-only implementation of the localPageRank
edgelist_weight_t localPageRank_weight(edgelist_weight_t &A, double c, double epsilon=1e-5,
                            int max_iters=200, bool return_only_neighbours=false);
#endif
