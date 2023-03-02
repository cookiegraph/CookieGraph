import networkx as nx
import re
import traceback
from .utils import * 

def get_script_content_features(G, df_graph, node, ldb):

  """
  Function to extract script content features (specified in features.yaml file)

  Args:
    node: URL of node
    G: networkX graph
    df_graph: DataFrame representation of graph
    ldb: content LDB
  Returns:
    List of script content features
  """

  keywords_fp = ["CanvasRenderingContext2D", "HTMLCanvasElement", "toDataURL", "getImageData", "measureText", "font", "fillText", "strokeText", "fillStyle", "strokeStyle", "HTMLCanvasElement.addEventListener", "save", "restore"]
  ancestors = nx.ancestors(G, node)
  ascendant_script_has_eval_or_function = 0
  ascendant_script_has_fp_keyword = 0
  ascendant_script_length = 0
  max_length = 0

  try:
    for ancestor in ancestors:
      try:
        if nx.get_node_attributes(G, 'type')[ancestor] == 'Script':
          content_hash = df_graph[(df_graph['dst'] == ancestor) & (df_graph['content_hash'] != "N/A")]["content_hash"]
          if len(content_hash) > 0:
            ldb_key = content_hash.iloc[0]
            ldb_key = bytes(ldb_key, 'utf-8')
            script_content = ldb.get(ldb_key)
            if len(script_content) > 0:
              script_content = script_content.decode('utf-8')
              script_length = len(script_content)
              if script_length > max_length:
                ascendant_script_length = script_length
                max_length = script_length
              if 'eval' in script_content or 'function' in script_content:
                ascendant_script_has_eval_or_function = 1
              for keyword in keywords_fp:
                if keyword in script_content:
                  ascendant_script_has_fp_keyword = 1
                  break
      except Exception as e:
        continue
  except Exception as e:
    print(e)

  sc_features = [ascendant_script_has_eval_or_function, ascendant_script_has_fp_keyword, \
              ascendant_script_length]
  sc_features_names = ['ascendant_script_has_eval_or_function', 'ascendant_script_has_fp_keyword', \
              'ascendant_script_length']

  return sc_features, sc_features_names


def get_ne_features(G):

    num_nodes = len(G.nodes)
    num_edges = len(G.edges)
    num_nodes_div = num_nodes
    num_edges_div = num_edges
    if num_edges == 0:
      num_edges_div = 0.000001
    if num_nodes == 0:
      num_nodes_div = 0.000001
    nodes_div_by_edges = num_nodes/num_edges_div
    edges_div_by_nodes = num_edges/num_nodes_div
    ne_features = [num_nodes, num_edges, nodes_div_by_edges, edges_div_by_nodes]
    ne_feature_names = ['num_nodes', 'num_edges', 'nodes_div_by_edges', 'edges_div_by_nodes']

    return ne_features, ne_feature_names

def get_connectivity_features(G, df_graph, node):

  connectivity_features = []

  in_degree = 0
  out_degree = 0
  in_out_degree = 0
  ancestors = 0
  descendants = 0
  closeness_centrality = 0
  average_degree_connectivity = 0
  eccentricity = 0
  ascendant_has_ad_keyword = 0
  clustering = 0
  
  is_parent_script = 0
  is_ancestor_script = 0
  descendant_of_eval_or_function = 0

  try:

    in_degree = G.in_degree(node)
    out_degree = G.out_degree(node)
    in_out_degree = in_degree + out_degree
    ancestor_list = nx.ancestors(G, node)
    ancestors = len(ancestor_list)
    descendants = len(nx.descendants(G, node))
    parents = list(G.predecessors(node))
    is_eval_or_function = 0

    for parent in parents:
      try:
        if nx.get_node_attributes(G, 'type')[parent] == 'Script':
          is_parent_script = 1
          break
      except:
        continue

    for ancestor in ancestor_list:
      try:
        if nx.get_node_attributes(G, 'type')[ancestor] == 'Script':
          is_ancestor_script = 1
          break
      except:
        continue

    for ancenstor in ancestor_list:
      try:
        if 'Element' in ancenstor:
          eval_attr = json.loads(G.nodes[ancestor]['attr']).get('eval')
          if eval_attr:
            descendant_of_eval_or_function = 1
            break
      except:
        continue
    
    ascendant_has_ad_keyword = ad_keyword_ascendants(node, G)
    closeness_centrality = nx.closeness_centrality(G, node)
    average_degree_connectivity = nx.average_degree_connectivity(G)[in_out_degree]
    clustering = nx.clustering(G, node)

    try:
      H = G.copy().to_undirected()
      eccentricity = nx.eccentricity(H, node)
    except Exception as e:
      eccentricity = -1

    connectivity_features = [in_degree, out_degree, in_out_degree, \
          ancestors, descendants, closeness_centrality, average_degree_connectivity, \
          eccentricity, clustering, is_parent_script, is_ancestor_script, \
          ascendant_has_ad_keyword,
          descendant_of_eval_or_function]
  
  except Exception as e:

    print("Error in connectivity features:", e)
    traceback.print_exc()
    connectivity_features = [in_degree, out_degree, in_out_degree, \
          ancestors, descendants, closeness_centrality, average_degree_connectivity, \
          eccentricity, clustering, is_parent_script, is_ancestor_script, \
          ascendant_has_ad_keyword,
          descendant_of_eval_or_function]

  connectivity_feature_names = ['in_degree', 'out_degree', 'in_out_degree', \
          'ancestors', 'descendants', 'closeness_centrality', 'average_degree_connectivity', \
          'eccentricity', 'clustering', 'is_parent_script', 'is_ancestor_script', \
          'ascendant_has_ad_keyword', \
          'descendant_of_eval_or_function']

  return connectivity_features, connectivity_feature_names


def get_structure_features(G, df_graph, node, ldb):

  all_features = []
  all_feature_names = []
  ne_features = []
  ne_feature_names = []
  connectivity_features = []
  connectivity_feature_names = []
  sc_features = []
  sc_features_names = []
  
  ne_features, ne_feature_names = get_ne_features(G)
  connectivity_features, connectivity_feature_names = get_connectivity_features(G, df_graph, node)
  #sc_features, sc_features_names = get_script_content_features(G, df_graph, node, ldb)

  all_features = ne_features + connectivity_features + sc_features
  all_feature_names = ne_feature_names + connectivity_feature_names + sc_features_names

  return all_features, all_feature_names

