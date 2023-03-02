import pandas as pd
import json
import networkx as nx
from yaml import load, dump
import os

import feature_scripts_cookies as fs

def extract_graph_node_features(G, df_graph, G_indirect, df_indirect_graph, G_indirect_all,
  node, ldb, selected_features, vid):

  all_features = []
  all_feature_names = ['visit_id', 'name']
  content_features = []
  structure_features = []
  dataflow_features = []
  additional_features = []
  content_feature_names = []
  structure_feature_names = []
  dataflow_feature_names = []
  additional_feature_names = []

  if 'content' in selected_features:
    content_features, content_feature_names = fs.get_content_features(G, df_graph, node)
  if 'structure' in selected_features:
    structure_features, structure_feature_names = fs.get_structure_features(G, df_graph, node, ldb)
  if 'dataflow' in selected_features:
    dataflow_features, dataflow_feature_names = fs.get_dataflow_features(G, df_graph, node, G_indirect, G_indirect_all, df_indirect_graph)
  if 'additional' in selected_features:
    additional_features, additional_feature_names = fs.get_additional_features(G, df_graph, node)

  all_features = content_features + structure_features + dataflow_features + additional_features
  all_feature_names += content_feature_names + structure_feature_names + \
                      dataflow_feature_names + additional_feature_names

  df = pd.DataFrame([[vid] + [node] + all_features], columns=all_feature_names)

  return df

def extract_graph_features(df_graph, G, vid, ldb, feature_config, first, tag):

    """
    Function to extract features.

    Args:
      df_graph_vid: DataFrame of nodes/edges for.a site
      G: networkX graph of site
      vid: Visit ID
      ldb: Content LDB
      feature_config: Feature config
    Returns:
      df_features: DataFrame of features for each URL in the graph

    This functions does the following:

    1. Reads the feature config to see which features we want.
    2. Creates a graph of indirect edges if we want to calculate dataflow features.
    3. Performs feature extraction based on the feature config. Feature extraction is per node of graph.
    """

    exfil_columns = ['visit_id', 'src', 'dst', 'dst_domain',
            'attr', 'time_stamp', 'direction', 'type']

    df_features = pd.DataFrame()
    nodes = G.nodes(data=True)
    G_indirect = nx.DiGraph()
    G_indirect_all = nx.DiGraph()
    df_indirect_graph = pd.DataFrame()

    df_graph['src_domain'] = df_graph['src'].apply(fs.get_domain)
    df_graph['dst_domain'] = df_graph['dst'].apply(fs.get_domain)
   
    selected_features = feature_config['features_to_extract']

    if 'dataflow' in selected_features:
      G_indirect, G_indirect_all, df_indirect_graph = \
          fs.pre_extraction(G, df_graph, ldb)
      if not os.path.exists("exfils_" + str(tag) + ".csv"):
        df_indirect_graph.reindex(columns=exfil_columns).to_csv("exfils_" + str(tag) + ".csv")
        #df_indirect_graph.to_csv("exfils_" + str(tag) + ".csv")
      else:
        df_indirect_graph.reindex(columns=exfil_columns).to_csv("exfils_" + str(tag) + ".csv", mode='a', header=False)
        #df_indirect_graph.to_csv("exfils_" + str(tag) + ".csv", mode='a', header=False)

    for node in nodes:
      #Currently, we filter out Element and Storage nodes since we only want to classify URLs (the other nodes are used for feature calculation for these nodes though)
      if ("type" in node[1]) and (node[1]["type"] == "Storage") and ('Cookie' in node[1]['attr']):
        #try:
        df_feature = extract_graph_node_features(G, df_graph, G_indirect, \
          df_indirect_graph, G_indirect_all, node[0], ldb, \
          selected_features, vid)
        df_features = df_features.append(df_feature)
        #except Exception as e:
        #  print('Error is:', e.__class__, e)
    
    return df_features
