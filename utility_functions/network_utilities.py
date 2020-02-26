import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


### Generates a random network of n nodes (the first one corresponds to earth)
### r = max distance

def generate_network(n,r_max,polar = False):
    
    r = np.random.rand(n,1)*r_max
    r[0] = 0 #Earth
    theta = np.random.rand(n,1)*4*np.pi - 2*np.pi
    phi = np.random.rand(n,1)*4*np.pi - 2*np.pi
    
    if polar==True:
        return np.hstack((r,theta,phi))  #polar coordinates
    
    x = r * np.cos(theta) * np.sin(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(phi)
    
    return np.hstack((x,y,z))   #cartesian coordinates


def plot_network(nodes):
    
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(nodes[1:,0],nodes[1:,1],nodes[1:,2])
    ax.scatter(nodes[0,0],nodes[0,1],nodes[0,2],color="red",s=100)   #Earth
    plt.show()

## disable some links for a certain amount of time
##
## delta_t = time between steps (in seconds)
##
## modes:
## light mode: few links, short time
## heavy mode: few links, long time
## unstable mode: many links, short time
## extreme mode: many links, long time
##
## priority: random, near, far
## prioritize disabling of links involving nodes near or far from Earth
## 
## custom_n_targets = number of targets
## custom_offtimes: array containing possible values for off times (in seconds)

def disable_links(A,total_time,delta_t,mode="light",priority="random", custom_n_targets = None, custom_offtimes = None):

    n = A.shape[0]
    n_updates = int(np.ceil(total_time/delta_t))
    time_max = np.max(A[0,:][np.isfinite(A[0,:])])    #propagation time from the furthest node to Earth, used as a reference
    
    At = np.repeat(A[:, :, np.newaxis], n_updates, axis=2) #add temporal dimension

    sorted_nodes = np.argsort(A[0,:])
    t_nodes = np.arange(n)
    
    if priority == "random":
        np.random.shuffle(t_nodes)   #nodes targeted for link removal
    elif priority == "near":
        t_nodes = sorted_nodes[:int(np.ceil(n/3))]
    elif priority == "far":
        t_nodes = np.flip(sorted_nodes)[:int(np.ceil(n/3))]
    
    possible_links = []
    possible_links = np.array([[x,y] for x in t_nodes for y in range(n) if x!=y if A[x,y]!=np.inf if [y,x] not in possible_links])

    if mode == "light":  
        rate = possible_links.shape[0] * 0.05  #disable 5% of possible links every time_max 
        offtimes = [time_max * 0.5]   #selected links stay off for around 0.5 * time_max
            
    elif mode == "heavy":
        rate = possible_links.shape[0] * 0.05  #disable 5% of possible links every time_max 
        offtimes = [time_max * 2]   #selected links stay off for around 2 * time_max
        
    elif mode == "unstable":
        rate = possible_links.shape[0] * 0.2  #disable 20% of possible links every time_max 
        offtimes = [time_max * 0.25]   #selected links stay off for around 0.25 * time_max
        
    elif mode == "extreme":
        rate = possible_links.shape[0] * 0.2  #disable 20% of possible links every time_max 
        offtimes = [time_max * 2]   #selected links stay off for around 2 * of time_max
    
    else:   #use light mode in case of a wrong "mode" value
        print("Wrong value for \"mode\", light mode will be used")
        rate = possible_links.shape[0] * 0.05  #disable 5% of possible links every time_max 
        offtimes = [time_max * 0.5]   #selected links stay off for around 0.5 * time_max
        
    n_targets = int(np.ceil(rate * total_time/time_max))
    
    if custom_n_targets != None:
        n_targets = custom_n_targets
    if custom_offtimes != None:
        offtimes = custom_offtimes
 
    indexes = np.random.choice(possible_links.shape[0], n_targets)
    disabled_links = possible_links[indexes,:]
    
    for link in disabled_links:
        start = np.random.randint(0,n_updates)
        end = start + int(np.ceil(np.random.choice(offtimes) / delta_t))  #offtime expressed in number of updates
        
        if(False):   # TEST
            print(link)
            print("start {}".format(start))
            print("end {}".format(end))
        At[link[0],link[1],start:min(end, n_updates)] = At[link[1],link[0],start:min(end, n_updates)] = np.inf 
            
    return At

### Creates the weighted adjacency matrix of the network
### Entries represent propagation times between nodes
def adjacency_matrix(nodes, tau_max, c = 3e8):
    
    n1 = nodes[:, np.newaxis, :]
    n2 = nodes[np.newaxis, :, :]
    
    A = np.linalg.norm(n1-n2, axis = 2)/c
    A[A>tau_max] = np.inf
    
    return A