from six.moves.urllib.parse import urlparse, parse_qs
from sklearn import preprocessing
import re
import json

def get_url_features(url, node_dict):

  """
  Function to extract URL features (specified in features.yaml file)

  Args:
    url: URL of node
    top_level_url: Top level URL
  Returns:
    List of URL features
  """

  keyword_raw = ["ad", "ads", "advert", "popup", "banner", "sponsor", "iframe", "googlead", "adsys", "adser", "advertise", "redirect",
                 "popunder", "punder", "popout", "click", "track", "play", "pop", "prebid", "bid", "pb.min", "affiliate", "ban", "delivery",
                 "promo","tag", "zoneid", "siteid", "pageid", "size", "viewid", "zone_id", "google_afc" , "google_afs"]
  keyword_char = [".", "/", "&", "=", ";", "-", "_", "/", "*", "^", "?", ";", "|", ","]
  screen_resolution = ["screenheight", "screenwidth", "browserheight", "browserwidth", "screendensity", "screen_res", "screen_param", "screenresolution", "browsertimeoffset"]
  
  try:
    parsed_url = urlparse(url)
    query = parsed_url.query
    params = parsed_url.params
    is_valid_qs = 1
    base_domain = node_dict['domain']
    top_level_domain = node_dict['top_level_domain']
  
  except:
    top_level_domain = ""
    base_domain = ""
    query = ""
    params = ""
    is_valid_qs = 0

  parsed_query = parse_qs(query)
  parsed_params = parse_qs(params)
  num_url_queries = len(parsed_query)
  num_url_params = len(parsed_params)
  num_id_in_query_field = len([x for x in parsed_query.keys() if "id" in x])
  num_id_in_param_field = len([x for x in parsed_params.keys() if "id" in x])

  is_third_party =0

  if (len(base_domain) > 0) and (base_domain != top_level_domain):
    is_third_party = 1

  semicolon_in_query = 0
  semicolon_in_params = 0
  base_domain_in_query = 0
  if len(base_domain) > 0 and base_domain in query:
    base_domain_in_query = 1
  if ";" in query:
    semicolon_in_query = 1
  if ";" in params:
    semicolon_in_params = 1

  screen_size_present = 0
  for screen_key in screen_resolution:
    if screen_key in query.lower() or screen_key in params.lower():
      screen_size_present = 1
      break
  ad_size_present = 0
  ad_size_in_qs_present = 0
  pattern = '\d{2,4}[xX]\d{2,4}'
  if re.compile(pattern).search(url):
    ad_size_present = 1
  if re.compile(pattern).search(query):
    ad_size_in_qs_present = 1

  keyword_char_present = 0
  keyword_raw_present = 0

  for key in keyword_raw:
    key_matches = [m.start() for m in re.finditer(key, url, re.I)]

    for key_match in key_matches:
      keyword_raw_present = 1
      if url[key_match - 1] in keyword_char:
        keyword_char_present = 1
        break
    if keyword_char_present == 1:
      break

  url_features = [is_valid_qs, num_url_queries, num_url_params, num_id_in_query_field, \
                  num_id_in_param_field, is_third_party, base_domain_in_query, \
                  semicolon_in_query, semicolon_in_params, screen_size_present, \
                  ad_size_present, ad_size_in_qs_present, keyword_raw_present, \
                  keyword_char_present]

  url_feature_names = ['is_third_party', 'base_domain_in_query', \
                  'semicolon_in_query', 'semicolon_in_params', 'screen_size_present', \
                  'ad_size_present', 'ad_size_in_qs_present', 'keyword_raw_present', \
                  'keyword_char_present']

  return url_features, url_feature_names

def get_node_features(node_name, node_dict, le):

  """
  Function to extract node features (specified in features.yaml file)

  Args:
    node_name: URL of node
    node_attr: Attribute of node (CPT/top level URL)
    le: LabelEncoding for node type
  Returns:
    List of node features
  """

  node_features = []
  name_length = 0
  
  try:

    name_length = len(node_name)
    node_features = [name_length]
    
  except Exception as e:
    print('Error node features:', e)
    node_features = [name_length]

  node_feature_names = ['name_length']
  
  return node_features, node_feature_names

def get_content_features(G, df_graph, node):

  le = preprocessing.LabelEncoder()
  le.fit(["Request", "Script", "Document", "Element", "Storage"])

  all_features = []
  all_feature_names = []
  node_features, node_feature_names = get_node_features(node, G.nodes[node], le)
  url_features, url_feature_names = get_url_features(node, G.nodes[node]) 
  all_features = node_features + url_features
  all_feature_names = node_feature_names + url_feature_names

  return all_features, all_feature_names
  