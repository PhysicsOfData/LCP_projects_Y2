import numpy as np
import math
from classes import Packet, Node
from tqdm.notebook import tqdm

#used to check if the time exceeds the maximum time of the system
def check_time_step(A, time):
    
    max_time_step = A.shape[2]
    
    if time >= max_time_step:
        raise Exception("Maximum time limit exceded")

# used to check if the link becomes unavailable before the packet is fully transmitted
#weights = time series of the weight of the considered link
#start = starting time
#end = ending time
def check_interval(weights, start, end):
    return np.max(weights[int(start):int(end)]) != np.inf 

#finds the next useful interval to send the packet if the link is down
#current_time = earliest time when the packet can be sent
#delta_time = time interval 
#e2e = end to end delay
#distances = weights of the edge during time
def find_next_interval(current_time, delta_time, e2e, distances):
    
    current_delta = math.floor(current_time / delta_time)
    #the last timeslot has to be considered as well so ceil is needed
    ending_delta = math.ceil((current_time+e2e) / delta_time)
    
    #if we already have a good interval then the packet can be sent immediatly
    if check_interval(distances, current_delta, ending_delta):
        return current_time
    #otherwise iterate until a good interval is found
    else:
        #time of the first np.inf after current_time
        i = current_delta + np.argmin(distances[current_delta:ending_delta] != np.inf)
        
        #number of timesteps required to send a packet
        delta_e2e = np.ceil(e2e / delta_time)
        
        #keep increasing i while either the max length is reached or a good interval is found
        while not check_interval(distances, i, i + delta_e2e):
            if i + delta_e2e >= distances.shape[0]:
                raise Exception("One packet cannot be sent before the maximum time")
            i += 1
        
        return i * delta_time

#used to find the next node and the arrival times
def find_next(At, starting_node, previous, times, delta_time, starting_time, max_time, earth=0):
    
    result = earth
    current = earth
    good_until = [] 

    while current != starting_node:
        result = current
        current = int(previous[current])

        #time slot when the node is reached
        current_delta = math.floor(times[current]/delta_time)
        #evolution of the link between source and destination from current_delta onwards 
        future_evolution = At[current, result, current_delta:]

        #if the link is disabled in the future
        if np.max(future_evolution) == np.inf:
            #the maximum sending time is equal to the starting time + the remaining time after the packet arrived
            max_sending_time = starting_time + (current_delta + np.argmax(future_evolution == np.inf)) * delta_time - times[current] 
            good_until.append(max_sending_time)
        else:
            good_until.append(max_time)

    if times[result] > max_time:
        raise Exception("Maximum time reached")
        
    return result, times[result], min(good_until)

#performs a modified version of the dijkstra algorithm that adapts to this specific problem
#A = adjacency matrix
#starting_node = node sending the packet
#ttr = transmission time
#delta_time = timestep dimension
#earth = earth node
def DTN_dijkstra(A, starting_node, starting_time, ttr, tps, delta_time, earth = 0):
    
    N = A.shape[0]
    
    #setting the arrival time of the packet to each node to infinity
    distances = np.ones(N) * np.inf
    distances[starting_node] = starting_time
    max_time = A.shape[2] * delta_time
    
    current = starting_node
    visited_nodes = 0
    
    #previous step in the shortest path
    previous = np.ones(N)*(-1)
    previous[starting_node] = starting_node
    
    #if the source is the destination do nothing
    if current == earth:
        return starting_time, -1, np.inf 
    
    #keep going until the shortest path to earth is found
    while current != earth:
        
        #arrival time of the packet in the current node
        current_time = distances[current]
        #time slot of the packet arrival
        current_step = math.floor(current_time / delta_time)
        
        #checking if the packet arrives after the maximum time
        check_time_step(A, current_step)
        
        #arrival times to each node if the message started from current node
        new_dists = np.zeros(N)
        
        #compute the arrival time to each node
        for i in range(N):
            
            #computing e2e delay as tp + ttr
            tp = tps[current, i]
            
            if tp == np.inf:
                new_dists[i] = np.inf
            else:
                e2e = tp + ttr
            
                #finding out when the packet can leave the current node to reach the next one
                next_good = find_next_interval(current_time, delta_time, e2e, A[current, i, :])
            
                #finding out the arrival time of the packet to node i after passing from current
                new_dists[i] = next_good + e2e
        
        new_dists[current] = current_time
        
        #if the arrival time is improved then the previous node is changed
        previous[distances > new_dists] = current
        
        #setting the correct arrival time to each node
        distances = np.minimum(distances, new_dists)
        
        visited_nodes += 1
        sorting_indexes = np.argsort(distances)
        
        current = sorting_indexes[visited_nodes]
    
    return find_next(A, starting_node, previous, distances, delta_time, starting_time, max_time, earth)

    #returns the queues of packets at each node
def get_nodes(N, packets):
    
    #generate N empty queues
    queues = [[] for i in range(N)]
    
    #add every packet to the queue corresponding to its starting node
    for i in range(packets.shape[0]):
        pkt = Packet(i, packets[i,1])
        pkt.source = packets[i,0]
        queues[packets[i,0]].append(pkt)
    
    #generating the Node objects
    nodes = []
    for i in range(N):
        nodes.append(Node(queues[i], i))
    
    return nodes 

#function used to sort the nodes based on the one that has the packet that
#would arrive first to the next point
def sorting_function(node):
    
    #if no packet is queued then the node has to be placed at the end of the sorted array
    if len(node.packets) == 0:
        return np.inf
    else:
        return node.packets[0].arrival_time

#runs djikstra on each node assuming that a packet is queued and that
#it is sent as soon as the sender can send it
'''
nodes = list of Node objects
first_free_moment = array indicating the first available moment for a node to send/recieve 
a packet
'''
def dijkstra_on_nodes(A, nodes, first_free_moment, ttr, tps, delta_time, next_hops, valid):
    
    #for each node
    for source in range(len(nodes)):
        
        #if the node is not empty
        if len(nodes[source].packets) > 0:
            destination = nodes[source].packets[0].destination

            #if the previous route is still valid then just update next_hop and arrival_time
            if valid[source, destination] > first_free_moment[source]:
                next_hop = int(next_hops[source, destination])
                nodes[source].packets[0].next_hop = next_hop 
                nodes[source].packets[0].arrival_time = first_free_moment[source] + tps[source, next_hop] + ttr

            else: 
                #compute dijkstra on the first node of the queue
                next_hop, arrival_time, valid_until = DTN_dijkstra(
                    A, 
                    source, 
                    first_free_moment[source], 
                    ttr, 
                    tps,
                    delta_time, 
                    earth = destination 
                )
                #update the information of the packet based on dijikstra result
                nodes[source].packets[0].next_hop = int(next_hop)
                nodes[source].packets[0].arrival_time = arrival_time

                #update the best route from source to destination and its validity
                next_hops[source, destination] = next_hops[destination, source] = next_hop
                valid[source, destination] = valid[destination, source] = valid_until 

    return nodes, next_hops, valid

#checks if there is one node that is completely isolated from the rest
#note that this does not notify the case where two nodes are connected
#but are separated from the rest
def check_nodes_connectivity(tps):
    
    #matrix saying if an edge is up or not
    connectivity = tps
    
    #setting the diagonal to inf so later i can check if a whole column is equal to inf
    connectivity[connectivity == 0] = np.inf
    
    #if there is a column that contains only inf it means that the node is disconnected
    if np.max(np.min(connectivity, axis = 1)) == np.inf:
        raise Exception("At least one of the nodes is never connected to the graph")
    
#packets = source and destination of every packet
def greedy_routing(A, packets, ttr, delta_time, with_tqdm=False):
    
    if with_tqdm:
        pbar = tqdm(total = packets.shape[0])

    tps = np.min(A, axis = 2)
    check_nodes_connectivity(tps)
    N = A.shape[0]
    nodes = get_nodes(N, packets)
    #at the beginning all of the nodes can transmit a packet theoretically
    first_free_moment = np.zeros(N)

    #data needed to save some computation
    #cell i,j constains the best next hop between i and j
    next_hops = np.ones((N, N)) * (-1) 
    #defines for how long the path will be the best
    valid = np.ones((N, N)) * (-1) 

    #number of packets that reached their destinatio
    arrived_packets = 0
    final_packets = []
    
    #while some packets aren't arrived yet
    while arrived_packets != packets.shape[0]:
        #find out the next step and the arrival time of all the first packets in the queues
        nodes, next_hops, valid = dijkstra_on_nodes(A, nodes, first_free_moment, ttr, tps, delta_time, next_hops, valid)
        #sort the nodes from the one that has the packet that would reach first the next hop
        nodes.sort(key = sorting_function)
        #packet to be eventually sent
        pts = nodes[0].packets[0]
        
        #boolean value that tells if the packet was sent or not
        sent = False
        
        #propagation time from current node to next hop
        tp = tps[pts.next_hop, nodes[0].id]
        #if the first bit of the packet reaches the reciever when the reiever is free
        if first_free_moment[pts.next_hop] <= pts.arrival_time - ttr:
            
            #set the reciever as busy until the packet is fully arrived
            first_free_moment[pts.next_hop] = pts.arrival_time
            #set the sender as busy until the packet is fully sent
            first_free_moment[nodes[0].id] = pts.arrival_time - tp            
            sent = True
            #send the packet by removing it from the sender queue
            nodes[0].packets.pop(0)

        else:
            #if the reciever is not free set the sender as busy until it is sure that 
            #when he sends the reciever will be idle
            first_free_moment[nodes[0].id] = first_free_moment[pts.next_hop] - tp + 1e-7
        
        #sort the nodes back by id in order to add the packet to the reciever queue
        nodes.sort(key = lambda node: node.id)
        
        #if a packet was sent
        if sent:
            
            pts.route.append(pts.next_hop)
            pts.arrival_times.append(pts.arrival_time)
            
            #if the packet reached its destination then remove it from the system
            if pts.next_hop == pts.destination:
                arrived_packets += 1
                final_packets.append(pts)

                if with_tqdm:
                    pbar.update(1)
            
            #else append it to the queue of the reciever
            else:
                nodes[pts.next_hop].packets.append(pts)
                
    if with_tqdm:
        pbar.close()

    return final_packets
