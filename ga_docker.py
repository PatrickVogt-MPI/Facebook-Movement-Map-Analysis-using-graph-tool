import gc_docker as gc
from graph_tool import *
from graph_tool.topology import all_paths
from graph_tool.generation import complete_graph
from timeit import default_timer as timer
from itertools import islice

def print_graph_info(g):
    '''
    Prints path to file, number of nodes and number of edges of graph.

    Args:
        g: graph object
    '''
    file       = g.gp.file
    n_vertices = len(list(g.vertices()))
    n_edges    = len(list(g.edges()))
    
    seperator_length = max(len(f'Graph data file: {file}'), len(f'Number of nodes: {n_vertices}'), len(f'Number of edges: {n_edges}'))   
    print()
    print(f'Graph data file: {file}')
    print('-'*seperator_length)
    print(f'Number of nodes: {n_vertices}')
    print(f'Number of edges: {n_edges}')

def print_connection_info(g):
    '''
    Lists number of nodes of every degree in the graph and their relative occurance frequency

    Args:
        g: graph object
    '''
    degree = [vertex.out_degree()+vertex.in_degree() for vertex in g.vertices()]
    for i in range(1, max(degree)+1):
        print(f'Number of nodes of degree {i}: {degree.count(i)} | {"{:.2%}".format(degree.count(i)/len(list(g.vertices())))}')
    print()
        
def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)
    
if __name__ == '__main__':   
    for g in graphs:
        print_graph_info(g)  
    