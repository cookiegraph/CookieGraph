# Collecting Data
To collect data for feature extraction and classifier, first run the customized version of OpenWPM. A sample demo.py file is given which crawls sites sampled from top-100K sites (top 1K and 9K from 1K-100K). The demo file checkpoints after 1000 sites to ensure the crawl is recoverable in case of a malfunction. See the README file included in the OpenWPM folder for more information.

# Feature extraction
To extract features from the collected dataset, run the ```run.py``` file in ```Feature Extraction and Classfication``` folder. The feature extraction pipeline will extract the relevant features and construct the graph required for classification pipeline.

# Classification
Before running the classification pipeline, conflict resolution for labels has to be run which makes sure that the labels for cookie nodes are propagated to same scripts writing first-party cookies on other sites which are not included in the ground truth. To run conflict resolution, first run ```find_commmon_scripts.py``` and then run ```identifier_cookies.py```. Finally run the code in the jupyter notebook provided in the conflict resolution folder.

To run classification, run the ```classify.py``` file in the classification folder.

