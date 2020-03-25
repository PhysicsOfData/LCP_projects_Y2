import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import collections as mc
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation

#returns a list of active links
def get_links(A,nodes):
    n = A.shape[0]
    return [np.array([nodes[i],nodes[j]]).T for i in range(n) for j in range(i+1) if A[i,j]!=np.inf]

#checks if a link is active 
def check_active(link, link_list):
    for x in link_list:
        if np.array_equal(x, link):
            return True
    return False

def update_lines(num, dataLines, lines, active_links, title) :

    title.set_text("Time = {}".format(num))
    
    for line, data in zip(lines, dataLines) :
        line.set_data(data[0:2, :])
        line.set_3d_properties(data[2, :])
        line.set_color("black")
        if not check_active(data, active_links[num]):
              line.set_color("red")
    return lines

def get_vel(node1, node2, c=3e8):
    diff = node2 - node1
    dist = np.linalg.norm(diff)
    time = dist/c
    vel = diff/time
    return vel

def update_graph(num,graph,coord,coord_nodes,start_times,arrival_times,step,n_pkt,vel,path,done,title,speed=3):
    
    time = num * speed
    
    for i in range(n_pkt):
        if done[i]:
            continue
  
        start = start_times[i][step[i]]
        end = arrival_times[i][step[i]]
        
        if time < start:
            status = "waiting"
        elif start <= time <= end:
            status = "midair"
        elif time > end:
            status = "arrived"
            
        if status == "midair":
            coord[i,:] = coord[i,:] + vel[i,:] * speed    
        elif status == "waiting":
            pass
        elif status == "arrived":
            try:
                step[i] += 1
                vel[i,:] = get_vel(coord_nodes[path[i][step[i]],:], coord_nodes[path[i][step[i]+1],:])
                start = start_times[i][step[i]]
                end = arrival_times[i][step[i]]
            except IndexError:   #no more steps
                done[i] = True

    
    graph._offsets3d = (coord[:,0],coord[:,1],coord[:,2])
    title.set_text("Time = {}".format(num))