import numpy as np
import math

#check if the link is okay, return true if the link is up, false otherside
# t = current time
# sender = node that sends packets
#receiver = node that recives packets
def check_link(At, sender,receiver,t, times):
    cell = int(t / times["slot"])
    return At[sender, receiver, cell] != np.inf

def get_propagation_times(At):
    return np.min(At, axis = 2)

#return True if the packet arrives, the packet will be discarded that happens 
#because the link fails during the propagation time + transmission time
# t = current time
# sender = node that sends packets
#receiver = node that recives packets
def is_arrive(At, sender, receiver, t, times):
    propagation_t = times["tp"][sender, receiver]
    total_time = times["ttx"] + propagation_t + t
    
    if total_time > At.shape[2]*times["slot"]:
        raise Exception('I want more information about the next interval time')
        
    initial_cell = int(t / times["slot"])
    final_cell = int(math.ceil(total_time / times["slot"]))
    return np.max(At[sender, receiver, initial_cell:final_cell]) != np.inf


# update vulnerable_time in this way: if the link is okay set the vunerable_time 
#for the sender,if the packet arrives set the vulnerable_time for receiver
# t = current time
# sender = node that sends packets
#receiver = node that recives packets
def set_vulnerable_time(At, sender, receiver, t, times):
    
    vulnerable_sender = t
    
    vulnerable_receiver = times["vulnerable"][receiver]
    
    if is_arrive(At, sender,receiver,t, times):
        vulnerable_sender = max(t, vulnerable_receiver - times["tp"][sender, receiver] - times["ttx"])
        vulnerable_receiver = max(t + times["tp"][sender, receiver], vulnerable_receiver + times["ttx"])
    
    
    return vulnerable_sender, vulnerable_receiver

        
#check before starts the transmission there are same collision of one 
#packet on sender and resciver side
#return boolean value
# t = current time
# sender = node that sends packets
#receiver = node that recives packets
def is_collision(sender, receiver, t, times):
    
    propagation_t = times["tp"][sender, 0]
    t_receiver = t + propagation_t
    
    #if the starting time is withing a transmission time from the vulnerable time
    #then a collision occurs
    
    transmission_collision = abs(t - times["vulnerable"][sender]) < times["ttx"]
    receive_collision = abs(t_receiver - times["vulnerable"][receiver]) < times["ttx"]
    
    return transmission_collision or receive_collision



#send the packets to ather nodes,update n_packet and packet_trace
#if the link is okay and the packet reaches destination
# x = sender node in adjacent matrix

def add_packet(At, t, sender, times, n_packet, packet_trace):

    n_node_tot = At.shape[0]
    gen = [i for i in range(1,n_node_tot) if i != sender]
    for receiver in gen:
        packets = n_packet[sender]
        time_1 = t
        time = t
        packet_counter = 1
        for packet in packets:
            if (
                    not packet in packet_trace[receiver] and 
                    check_link(At, sender, receiver, time, times) and 
                    not is_collision(sender, receiver, time, times)
               ):
                times["vulnerable"][[sender,receiver]] = set_vulnerable_time(
                    At, 
                    sender,
                    receiver,
                    t, 
                    times
                )

                if is_arrive(At, sender,receiver,time, times):
                    
                    n_packet[receiver].append(packet)
                    packet_trace[receiver].append(packet)
                    
                    #using receiver-1 because packet_time does not contain the earth
                    tp = times["tp"][sender, receiver]
                    ttx = times["ttx"]
                    
                    if (times["packet"][packet][receiver-1] == 0):
                        times["packet"][packet][receiver-1] = packet_counter*ttx + tp + time_1
                    else:
                        new_time = times["packet"][packet][receiver-1] + packet_counter*ttx + tp
                        times["packet"][packet][receiver-1] = new_time
                    time = time + times["ttx"]
                    
                    packet_counter += 1
    return times["vulnerable"], n_packet, packet_trace, times["packet"]
                    
                    
                    
#send the packets to earth if the link is up and update n_packet
# x = sender node in adjacent matrix
def arrive_to_earth(At, t, sender, times, n_packet, packet_trace, packet_arrive):
    
    packets = n_packet[sender]
    time = t
    packet_counter = 1
    for packet in packets:
        if not is_collision(sender, 0, time, times):
            times["vulnerable"][[sender, 0]] = set_vulnerable_time(At, sender, 0, time, times)
            
            if is_arrive(At, sender, 0, time, times):
                n_packet[sender].remove(packet)
                n_packet[0].append(packet)
                  
                packet_arrive.append(int(packet))
                ttx = times["ttx"]
                tp = times["tp"][sender, 0]
                new_time = times["packet"][packet,sender-1] + packet_counter * ttx + tp 
                times["packet"][packet][sender-1] = new_time
                time = time + times["ttx"]
                packet_counter += 1
                
    return times["vulnerable"], n_packet, packet_trace, packet_arrive, times["packet"]


# At = adjacent matrix
# A = propagation matrix
# ttr = trasmission time
# delta_time = slot_time
# packets

def convert_packets(packets, n_nodes):
    
    n_packet = [[] for _ in range(n_nodes)]
    for i in range(len(packets)):        
        n_packet[packets[i,0]].append(i)

    return n_packet

# n_packet = every list is the code of node with the same index, and contains the ID packet that we want to send
# n_node_tot = number of nodes, in our case is 10 including the earth
# packet_trace = keep the trace of the road followed by each package
# trasmision_time = time to trasmit a single packet
# packet_arrive = [ID number of packets arrive to earth]
# packet_arrive_dupl = [ID number of all packets arrive to earth]
# vulnerable_time = [start_time,  collect the vunlerable time for each node]
# slot_time = duration of each interval time
# packet_time = each list rappresent a single packet: the value is the time it takes to get to the earth, the index indicates
# from which node the packet is send to earth.
def epidemic(At, transmission_time, slot_time, packets):

    n_node_tot = At.shape[0]
    n_packet_tot = packets.shape[0] 
    n_packet = convert_packets(packets, n_node_tot) 
    #this is used to copy the list
    packet_trace = [queue[:] for queue in n_packet]
    
    packet_arrive = []
    vulnerable_time = np.zeros(n_node_tot)
    #slot_time = delta_time
    packet_time = np.zeros((n_packet_tot, n_node_tot-1))
    times = {
        "ttx": transmission_time,
        "vulnerable": vulnerable_time,
        "slot": slot_time,
        "packet": packet_time,
        "tp": get_propagation_times(At) 
    }


    #start time
    for t in np.arange(0,At.shape[2]*slot_time,transmission_time):

        #if all packet are received exit the cycle
        if len(n_packet[0]) == n_packet_tot:
            return packet_arrive, packet_time, times["vulnerable"]

        for i in range(1, n_node_tot):
            #print('tempo che scorre',t)
            if len(n_packet[i]) != 0:
                if t != 0:
                    for p in n_packet[i]:
                        if packet_time[p, i-1] <= t:
                            packet_time[p, i-1] += transmission_time
            
                # if the link to erath is down 
                if not check_link(At, i, 0, t, times):
                    if ( (t >= vulnerable_time[i] + transmission_time) == True):
                    
                        times["vulnerable"], n_packet, packet_trace, times["packet"] = add_packet(
                                At,
                                t,
                                i, 
                                times,
                                n_packet,
                                packet_trace
                        )
                    
                else:
                
                    if t >= vulnerable_time[i] + transmission_time:
                    
                        #this is all just one line
                        times["vulnerable"], n_packet, packet_trace, packet_arrive, times["packet"] = arrive_to_earth(
                                At,
                                t,
                                i,
                                times,
                                n_packet,
                                packet_trace,
                                packet_arrive
                        )
                    
        if len(n_packet) == 0:
            break

    return packet_arrive, packet_time, times["vulnerable"]
