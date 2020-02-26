from scipy.sparse.csgraph import dijkstra
###DELAY FUNCTION###
# 
##This function takes in input 3 parameters: 
# 1) scheduling is defined as a list of lists in the sense that it is a list that contains the scheduling of 
#every node which corresponds to the istants of time a node has to forward packets that are in its queue. For 
#every node these "forwarding istants" are compactly put in a list.
# 2) routing is a slightly more complicated data structure; Here for every node we place a list whose elements 
#are the lists containg the hops that every packet in the queue of a specific node has to go through in order to 
#reach its destination
# 3) n_pkts is the total number of packets that has to be forwarded in our network

def delay(A, scheduling,routing,n_pkts, T_tx):

    #The waiting list is obtained as a result of the concatenation of all the lists present in scheduling
    waiting = [wait for node in scheduling for wait in node] 
    #The routes list instead of having all the forwarding times, it contains all the hops every pkt has to do
    routes = [path for node in routing for path in node]
    
    longest = 0
    
    for i in range(n_pkts):
        path = routes[i]
        #Here with tleft we are not taking into account the fact that a packet may be queued in some intermediate 
        #nodes on its remaining way to destination. Anyway this does not represent a problem given the fact that 
        #our scheduling provides us not just with the information about when a packet is sent from its 
        #source node but also all the instants it will be forwarded by intermediate nodes.
        #As we see tleft is made of the sum of transmission and propagation time for every remaining hop
        tleft = sum([T_tx + A[path[j],path[j+1]] for j in range(len(path)-1)]) 
        
        
        #The total time is given by the sum of the time we wait before forwarding and tleft which can be seen as
        #the minimum time it takes to go through the rest of the path
        t_tot = waiting[i] + tleft 
        
        #Here we are looking for the last packet to arrive at destination
        longest = max(longest,t_tot)  
    return longest

###deviations: given an optimal routing (that in our case is the one determined by Dijkstra) this function returns 
#the fraction of times a packet doesn't follow the route which was pre-established by the algorithm
def deviations(A, packets):
    
    indices = [packet.destination for packet in packets]
    _, predecessors = dijkstra(A, directed=False, indices=indices, return_predecessors=True)
    n_deviations = 0
    
    for packet in packets:
        #print(packets)
        route = packet.route
        correct = True
        for i in range(len(route) - 2, -1, -1):
            #if the route is correct from the second hop onward than it must
            #be correct because haveing additional hops would increase the distance
            #print(correct, route[i] != predecessors[packet.destination, route[i+1]])
            if correct and route[i] != predecessors[packet.destination, route[i + 1]]:
                correct = False
                n_deviations += 1


    return n_deviations/len(packets)

###throughput function
#the throughput enables us to evaluate the performance of our routing algorithm 
#the function returns the ratio between the number of packets sent and the total time elapsed
def throughput(n_pkts,delay):
    return n_pkts/delay