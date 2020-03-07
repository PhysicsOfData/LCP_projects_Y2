import pylab as pl
from matplotlib import collections  as mc
import matplotlib.pyplot as plt
import numpy as np
### pkt_plot function
#This function takes in input the times in which packets are recepted at destination and the transmission time
#It enables us to visualize the moments in which we receive packets
def pkt_plot(packets, t_tx, axs = None):
    recept_times = [x.arrival_time - t_tx for x in packets]
    end_recept = [x.arrival_time for x in packets]
    seg=[]
    for i in range(len(packets)-1):
        diff= recept_times[i+1]-end_recept[i]
        if diff>0:
            seg.append([(end_recept[i],0.1),(recept_times[i+1],0.1)])
    
    lines=[[(x,0),(x+t_tx,0)] for x in recept_times]
    
    colors=[(np.random.rand(),np.random.rand(),np.random.rand(),1) for x in packets]
    
    lc = mc.LineCollection(lines, linewidths=10,color=colors)
    if axs is None:
        _, axs = plt.subplots()

    axs.add_collection(lc)

    seg_c = mc.LineCollection(seg, linewidths=10,color="black")
    axs.add_collection(seg_c)
    axs.set_xlim(0,(recept_times[-1]+t_tx)*1.01)
    axs.set_ylim(-0.5,0.5)
    axs.set_yticks([])
    axs.set_xlabel("Time(s)")
    axs.set_title("Arrival time to earth of each packet")
    
    plt.show()
