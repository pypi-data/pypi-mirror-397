import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

class Node:
    def __init__(self,name,duration=0):
        self.name = name
        self.duration = duration
        # self.predecessors = []
        self.successors = []
        
        self.early_start = self.early_finish = self.latest_start = self.latest_finish = 0
        
    def add_successor(self,node):
        self.successors.append(node)
        node.predecessors.append(self)
        
    def node_summary(self):
        return f"Name : {self.name}, dur : {self.duration}, suc : {self.successors}"
        
    # def __repr__(self):
        # return "Node : ",self.name, " Duration : ",self.duration
        
        
class CriticalPathMethod:
    def __init__(self):
        self.nodes = {}
        self.probable_paths = []
        self.total_project_duration = -1
        self.duration_unit = "days" # By default Duration entired will be in days
        self.critical_path = []
        self.edges = []
        
    def add_activity(self,name,duration):
        if name not in self.nodes:
            self.nodes[name] = Node(name,duration)
            
    def add_activities_relations(self,activities,durations,prede):
        for i in range(0,len(activities)):
            self.add_activity(activities[i],durations[i])
            self.add_relation(activities[i],prede[i])
            
    def add_relation(self,cur,predes):
        
        for p in predes.split(','):
            p = p.strip()
            
            if p == '-':
                parent = self.nodes['O']
                parent.successors.append(cur)
            
            elif p in self.nodes:
                parent = self.nodes[p]
                parent.successors.append(cur)
            
    def find_probable_paths(self,cur=None,path=""):
        
        # print("Cur : ",cur)
        
        if cur is None:
            if 'O' in self.nodes:
                cur = self.nodes['O']
            else:
                return
        
        # if path == "":
            # path = str(cur.name)
        # else:
        path +=  str(cur.name)
            
        if len(cur.successors) == 0:
            path = [p for p in path]
            self.probable_paths.append(path)
            return
        for c in cur.successors:
            if c in self.nodes:
                self.find_probable_paths(self.nodes[c],path)
        # if(len(cur.successors) == 0):
        #     self.find_probable_paths.append(path)
    
    def find_critical_path(self,cur=None):
            
        for probable_path in self.probable_paths:
            if(sum(self.nodes[cur_node].duration for cur_node in probable_path) > self.total_project_duration):
                self.critical_path = probable_path
                self.total_project_duration = sum(self.nodes[cur_node].duration for cur_node in probable_path)
            elif(sum(self.nodes[cur_node].duration for cur_node in probable_path) == self.total_project_duration):
                self.critical_path.append(probable_path)
                
    def get_edges(self):
        for node in self.nodes:
            for suc in self.nodes[node].successors:
                    self.edges.append((self.nodes[node].name,suc,{'duration':self.nodes[node].duration}))
                
            if suc == []:
                self.edges.append((self.nodes[node].name,'T',{'duration':0}))
    
    def get_hierarchical_layout(self,graph, start_node):
        """
        Calculates node positions for a hierarchical layout.

        Args:
            graph (nx.Graph): The graph to lay out.
            start_node: The node to start the layout from (usually the root).

        Returns:
            dict: A dictionary of node positions {node: (x, y)}.
        """
        pos = {}
        levels = {}

        # 1. Determine the level of each node using BFS
        q = deque([(start_node, 0)])
        visited = {start_node}
        levels[start_node] = 0

        while q:
            node, level = q.popleft()
            neighbors = sorted(list(graph.neighbors(node))) # Sort for consistent layout
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    levels[neighbor] = level + 1
                    q.append((neighbor, level + 1))

        # 2. Group nodes by level
        nodes_by_level = {}
        for node, level in levels.items():
            if level not in nodes_by_level:
                nodes_by_level[level] = []
            nodes_by_level[level].append(node)

        # 3. Assign x, y coordinates
        for level, nodes in nodes_by_level.items():
            num_nodes_in_level = len(nodes)
            # Center the nodes vertically
            y_start = - (num_nodes_in_level - 1) / 2

            for i, node in enumerate(nodes):
                pos[node] = (level, y_start + i)

        return pos
    
    def display_network(self):
        G = nx.Graph()
        plt.figure(figsize=(10,4))
        G.add_edges_from(self.edges)    
        color_edges = []
        l = 'O'
        for c in self.critical_path:
                # print(c," --> ",end="")
            color_edges.append((l,c))
            l = c
        color_edges.append((self.critical_path[-1],'T'))  
        edges_colors = ['red' if ed in color_edges else 'black' for ed in G.edges()]
        
        initial_pos = {'O':(0,0),'T':(10,0)}

        fixed_nodes = ['O','T']

        pos = self.get_hierarchical_layout(G,'O')
        # nx.draw_networkx(G,pos,node_size=700,width=2,edge_color=edges_colors)
        
        nx.draw(G,pos,with_labels=True,node_size=700,edge_color=edges_colors,arrows=True,arrowstyle='-|>',arrowsize=20)
        
        edge_durations = nx.get_edge_attributes(G,'duration')
        
        nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_durations)


        plt.title("Network diagram with critical Path")
        plt.show()


    def network_summary(self):
        print("\n\n---------------Network Summary-----------------\n\n")
        print("Total number of Activities/Nodes : ",len(self.nodes))
        # print("Nodes : ",self.nodes)
        print("Nodes : ",end="")
        for c in self.nodes:
            print(c," ",end="")
            
        print("\nAll Probable Paths : ")
        for p in self.probable_paths:
            print(p)
        print("Critical Path : ",self.critical_path)
        print("Total project duration : ",self.total_project_duration)
        print("Duration unit :",self.duration_unit)
        print("Edges : ",self.edges)