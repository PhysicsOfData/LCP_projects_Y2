class Packet():
    
    def __init__(self, index ,destination):
        
        #final destination of the packet
        self.destination = destination
        
        #arrival time at the next hop
        self.arrival_time = -1
        
        #index of the next hop
        self.next_hop = -1
        
        #index that identifies the packet, used for debugging purposes
        self.id = index

        #starting node
        self.source = -1
        
        self.route = []
        
        self.arrival_times = []
    
    #function that is called when str(packet) is called
    def __str__(self):
        return f"id: {self.id}, next hop: {self.next_hop}, destination: {self.destination}"

class Node():
    
    def __init__(self, packets, index):
        
        #queue of the packets
        self.packets = packets
        
        #index of the node
        self.id = index
