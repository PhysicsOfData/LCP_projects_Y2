import pylab as pl
from matplotlib import collections  as mc
import matplotlib.pyplot as plt

### pkt_plot function
#This function takes in input the times in which packets are recepted at destination and the transmission time
#It enables us to visualize the moments in which we receive packets
def pkt_plot(packets,t_tx):
    recept_times = [x.arrival_time for x in packets]
    lines=[[(x,0),(x+t_tx,0)] for x in recept_times]
    cmap=["snow","blue","coral","yellow","green","black","rebeccapurple","sienna","navy","slategray"]
    colors=[cmap[x.source] for x in packets]
    lc = mc.LineCollection(lines, linewidths=10,color=colors)
    _, ax = plt.subplots()
    ax.add_collection(lc)
    
    ax.set_xlim(0,(recept_times[-1]+t_tx)*1.01)
    ax.set_ylim(-0.5,0.5)
    ax.set_yticks([])
    
    plt.show()