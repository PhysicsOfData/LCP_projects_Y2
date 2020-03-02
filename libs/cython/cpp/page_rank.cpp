#include <utility>
#include <vector>
#include <queue>
#include <iostream>
#include "page_rank.h"


// define class methods
queue_elem_t::queue_elem_t(int node, double weight){
  this->node = node;
  this->weight = weight;
}
bool queue_elem_t::operator>(const queue_elem_t& rhs) const{
  return this->weight > rhs.weight;
}
bool queue_elem_t::operator>=(const queue_elem_t& rhs) const{
  return this->weight >= rhs.weight;
}
bool queue_elem_t::operator<(const queue_elem_t& rhs) const{
  return this->weight < rhs.weight;
}
bool queue_elem_t::operator<=(const queue_elem_t& rhs) const{
  return this->weight <= rhs.weight;
}
bool queue_elem_t::operator==(const queue_elem_t& rhs) const{
  return this->weight == rhs.weight;
}
bool queue_elem_t::operator!=(const queue_elem_t& rhs) const{
  return this->weight != rhs.weight;
}


// c-type implementation of the push operation
bool_vec_t push(double_vec_t &p, double_vec_t &r,
                double alpha, int u, double du, nodelist_t &neighbours,
                                  double_vec_t &neighbours_deg, double epsilon){

  //update p and r
  p[u] += alpha*r[u];
  r[u] *= (1.0-alpha)/2.;

  // initialize r_above_th
  bool_vec_t r_above_th = bool_vec_t(neighbours.size(), false);

  for(size_t i=0; i<neighbours.size(); i++){
    int n = neighbours[i];
    r[n] += (1.0-alpha)*r[u]/(2.0*du);

    // if its a neighbour the degree cannot be 0
    if(r[n]/neighbours_deg[i] >= epsilon){
      r_above_th[i] = true;
    }
  }

  return r_above_th;
}

// c-type implementation of the approximateSimrank
double_vec_pair_t approximateSimrank(edgelist_t &A, int v, double alpha,
                    double epsilon, int max_iters, bool return_only_neighbours){

  size_t N = A.size();

  double_vec_t p = double_vec_t(N, 0.);
  double_vec_t r = double_vec_t(N, 0.);
  r[v] = 1;

  // this is a max-pq, as in the paper
  std::priority_queue<queue_elem_t, std::vector<queue_elem_t>> pq;
  pq.push(queue_elem_t(v, 1./A[v].size()));

  int iters = 0;
  while(pq.size()>0 && pq.top().weight >= epsilon && iters<max_iters){
    int u = pq.top().node;
    pq.pop();

    nodelist_t neigh = A[u];
    double_vec_t neigh_deg = double_vec_t(neigh.size(), 0);

    for(size_t i=0; i<neigh.size(); i++){
      neigh_deg[i] = A[neigh[i]].size();
    }

    bool_vec_t r_above_th = push(p, r, alpha, u, A[u].size(), neigh, neigh_deg, epsilon);

    for(size_t i=0; i<r_above_th.size(); i++){
      if(r_above_th[i]){
        int n = neigh[i];
        pq.push(queue_elem_t(n, r[n]/neigh_deg[i]));
      }
    }

    iters++;
  }

  if(!return_only_neighbours){
    return double_vec_pair_t(p, r);
  }else{
    double_vec_t p1 = double_vec_t(A[v].size(), 0.);
    double_vec_t r1 = double_vec_t(A[v].size(), 0.);

    for(size_t i=0; i<A[v].size(); i++){
      p1[i] = p[A[v][i]];
      r1[i] = r[A[v][i]];
    }
    return double_vec_pair_t(p1, r1);
  }
}


edgelist_weight_t localPageRank(edgelist_t &A, double c, double epsilon,
                                    int max_iters, bool return_only_neighbours){

  size_t N = A.size();
  edgelist_weight_t L = edgelist_weight_t(N);

  double alpha = 2*c/(1+c);
  // andersen's paper inverts alpha
  alpha = 1-alpha;

  for(size_t i=0; i<N; i++){
    // out = (p, r)
    double_vec_pair_t out = approximateSimrank(A, i, alpha,  epsilon, max_iters, return_only_neighbours);
    // create the new nodelist
    L[i] = nodelist_weight_t(A[i].size());

    //std::cout << "Computed p for node " << i <<": [";
    //for(double weight:std::get<0>(out)){
    //  std::cout << weight << ", ";
    //}
    //std::cout << "]" << std::endl;

    for(size_t k=0; k<A[i].size(); k++){
      if(return_only_neighbours){
        L[i][k] = edge_weight_t(A[i][k], std::get<0>(out)[k]);
        //std::cout << "adding edge: (" << std::get<0>(A[i][k]) << ", " << std::get<0>(out)[k] << ")";
        //std::cout << " for node: " << i << std::endl;
      }else{
        L[i][k] = edge_weight_t(A[i][k], std::get<0>(out)[A[i][k]]);
      }
    }

  }
  return L;
}

// weighted functions

// all of the functions below are defined using c-types
// they can be accessed through python using the python handler
// for localPageRank
double getDegree(nodelist_weight_t edges){
  double out = 0;
  for(edge_weight_t edge:edges){
    out += std::get<1>(edge);
  }
  return out;
}

// c-type implementation of the push operation
bool_vec_t push_weight(double_vec_t &p, double_vec_t &r,
                double alpha, int u, double du, nodelist_weight_t &neighbours,
                                  double_vec_t &neighbours_deg, double epsilon){

  //update p and r
  p[u] += alpha*r[u];
  r[u] *= (1.0-alpha)/2.;

  // initialize r_above_th
  bool_vec_t r_above_th = bool_vec_t(neighbours.size(), false);

  for(size_t i=0; i<neighbours.size(); i++){
    int n = std::get<0>(neighbours[i]);
    r[n] += (1.0-alpha)*r[u]/(2.0*du);

    // if its a neighbour the degree cannot be 0
    if(r[n]/neighbours_deg[i] >= epsilon){
      r_above_th[i] = true;
    }
  }

  return r_above_th;
}

// c-type implementation of the approximateSimrank
double_vec_pair_t approximateSimrank_weight(edgelist_weight_t &A, double_vec_t &degs, int v, double alpha,
                    double epsilon, int max_iters, bool return_only_neighbours){

  size_t N = A.size();

  double_vec_t p = double_vec_t(N, 0.);
  double_vec_t r = double_vec_t(N, 0.);
  r[v] = 1;

  // this is a max-pq, as in the paper
  std::priority_queue<queue_elem_t, std::vector<queue_elem_t>> pq;
  pq.push(queue_elem_t(v, 1./getDegree(A[v])));

  std::vector<int> v_neighs = std::vector<int>(A[v].size());
  for(size_t i=0; i<A[v].size(); i++){
    v_neighs[i] = std::get<0>(A[v][i]);
  }

  int iters = 0;
  while(pq.size()>0 && pq.top().weight >= epsilon && iters<max_iters){
    int u = pq.top().node;
    pq.pop();

    nodelist_weight_t neigh = A[u];
    double_vec_t neigh_deg = double_vec_t(neigh.size(), 0);
    double du = 0;

    for(size_t i=0; i<neigh.size(); i++){
      int n = std::get<0>(neigh[i]);
      du += std::get<1>(neigh[i]);
      neigh_deg[i] = degs[n];
    }

    bool_vec_t r_above_th = push_weight(p, r, alpha, u, du, neigh, neigh_deg, epsilon);

    for(size_t i=0; i<r_above_th.size(); i++){
      if(r_above_th[i]){
        int n = std::get<0>(neigh[i]);
        pq.push(queue_elem_t(n, r[n]/neigh_deg[i]));
      }
    }

    iters++;
  }

  if(!return_only_neighbours){
    return double_vec_pair_t(p, r);
  }else{
    double_vec_t p1 = double_vec_t(v_neighs.size(), 0.);
    double_vec_t r1 = double_vec_t(v_neighs.size(), 0.);

    for(size_t i=0; i<v_neighs.size(); i++){
      p1[i] = p[v_neighs[i]];
      r1[i] = r[v_neighs[i]];
    }
    return double_vec_pair_t(p1, r1);
  }
}


edgelist_weight_t localPageRank_weight(edgelist_weight_t &A, double c, double epsilon,
                                    int max_iters, bool return_only_neighbours){

  size_t N = A.size();
  edgelist_weight_t L = edgelist_weight_t(N);

  double alpha = 2*c/(1+c);
  // andersen's paper inverts alpha
  alpha = 1-alpha;

  // precompute the degrees for much faster computation
  double_vec_t degs = double_vec_t(N, 0.);
  for(size_t i = 0; i<degs.size(); i++)
    degs[i] = getDegree(A[i]);

  for(size_t i=0; i<N; i++){
    // out = (p, r)
    double_vec_pair_t out = approximateSimrank_weight(A, degs, i, alpha,  epsilon, max_iters, return_only_neighbours);
    // create the new nodelist
    L[i] = nodelist_weight_t(A[i].size());

    for(size_t k=0; k<A[i].size(); k++){
      if(return_only_neighbours){
        L[i][k] = edge_weight_t(std::get<0>(A[i][k]), std::get<0>(out)[k]);
        //std::cout << "adding edge: (" << std::get<0>(A[i][k]) << ", " << std::get<0>(out)[k] << ")";
        //std::cout << " for node: " << i << std::endl;
      }else{
        L[i][k] = edge_weight_t(std::get<0>(A[i][k]), std::get<0>(out)[std::get<0>(A[i][k])]);
      }
    }

  }
  return L;
}

/*
int main(){
  return 0;
}
*/
