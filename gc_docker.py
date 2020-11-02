import csv
from graph_tool import *
from graph_tool.util import find_vertex
import re
from pathlib import Path
from timeit import default_timer as timer

def create_movement_graphs_from_csv(path: Path, key: str = '', display_runtime: bool = False):  
    if(display_runtime): start = timer()
    
    pattern = '*' + key + '*.csv' if key else '*.csv'       
    csv_paths = [csv_path for csv_path in Path(path).glob(pattern)]    
    
    graphs = []
    
    for path in csv_paths:  
        with open(path, encoding='utf8') as csvfile:
            dict_reader = csv.DictReader(csvfile, delimiter=',')
            
            g = Graph()
            
            # Map graph properties
            g.gp.date_time = g.new_graph_property('string')
            g.gp.level     = g.new_graph_property('string')
            g.gp.tile_size = g.new_graph_property('int32_t')
            g.gp.file      = g.new_graph_property('string')
            
            # Map vertex properties
            g.vp.lat          = g.new_vertex_property('double')
            g.vp.lon          = g.new_vertex_property('double')
            g.vp.polygon_lat  = g.new_vertex_property('double')
            g.vp.polygon_lon  = g.new_vertex_property('double')
            g.vp.polygon_id   = g.new_vertex_property('int32_t')
            g.vp.polygon_name = g.new_vertex_property('string')
            g.vp.country      = g.new_vertex_property('string')
            #g.vp.quadkey      = g.new_vertex_property('int32_t')
            
            # Map edge properties
            g.ep.weight         = g.new_edge_property('double')
            g.ep.n_crisis       = g.new_edge_property('int32_t')
            g.ep.n_baseline     = g.new_edge_property('double')
            g.ep.length         = g.new_edge_property('double')
            g.ep.n_difference   = g.new_edge_property('double')
            g.ep.z_score        = g.new_edge_property('double')
            g.ep.percent_change = g.new_edge_property('double') 
            
            vertices = []
            
            for row in dict_reader:
                coordinates = re.findall(r"[-]?[0-9]*\.[0-9]*", row['geometry'])
                
                # Assign graph properties
                g.gp.date_time = row['date_time']
                g.gp.level     = row['level']
                g.gp.tile_size = int(row['tile_size'])
                g.gp.file      = path.name
                
                # Assign vertex properties
                start_lat = float(coordinates[1])
                start_lon = float(coordinates[0])
                start_coordinates = (start_lat, start_lon)
                
                if(not (start_coordinates in vertices)):
                    vertices.append(start_coordinates)
                    start_vertex = g.add_vertex()
                    
                    g.vp.lat[start_vertex]          = start_lat
                    g.vp.lon[start_vertex]          = start_lon
                    g.vp.polygon_lat[start_vertex]  = float(row['start_lat'])
                    g.vp.polygon_lon[start_vertex]  = float(row['start_lon'])
                    g.vp.polygon_id[start_vertex]   = int(row['start_polygon_id'])
                    g.vp.polygon_name[start_vertex] = row['start_polygon_name']
                    g.vp.country[start_vertex]      = row['country']
                    #g.vp.quadkey[start_vertex]      = int(row['start_quadkey'])
                else:
                    ind = vertices.index(start_coordinates)
                    start_vertex = g.vertex(ind)
                
                end_lat = float(coordinates[3])
                end_lon = float(coordinates[2])
                end_coordinates = (end_lat, end_lon)
                
                if(not (end_coordinates in vertices)):
                    vertices.append(end_coordinates)
                    end_vertex = g.add_vertex()
                    
                    g.vp.lat[end_vertex]          = end_lat
                    g.vp.lon[end_vertex]          = end_lon
                    g.vp.polygon_lat[end_vertex]  = float(row['end_lat'])
                    g.vp.polygon_lon[end_vertex]  = float(row['end_lon'])
                    g.vp.polygon_id[end_vertex]   = int(row['end_polygon_id'])
                    g.vp.polygon_name[end_vertex] = row['end_polygon_name']
                    g.vp.country[end_vertex]      = row['country']
                    #g.vp.quadkey[end_vertex]      = int(row['end_quadkey'])
                else:
                    ind = vertices.index(end_coordinates)
                    end_vertex = g.vertex(ind)
                
                # Assign edge properties               
                edge = g.add_edge(start_vertex, end_vertex)
                
                g.ep.n_crisis[edge]       = int(row['n_crisis'])
                g.ep.n_baseline[edge]     = float(row['n_baseline'])
                g.ep.length[edge]         = float(row['length_km'])
                g.ep.n_difference[edge]   = float(row['n_difference'])
                g.ep.z_score[edge]        = float(row['z_score'])
                g.ep.percent_change[edge] = float(row['percent_change'])
                
            # Assign probability weight
            for vertex in g.vertices():
                n_total = vertex.out_degree(g.ep.n_crisis)
                for edge in vertex.out_edges():
                    g.ep.weight[edge] = g.ep.n_crisis[edge]/n_total
                
            graphs.append(g)
    
    end = timer()
    if (display_runtime): print(f'Runtime Graph Creation: {end - start} seconds')
    
    return graphs if graphs else None
    
    
