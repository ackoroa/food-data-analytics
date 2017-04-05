import pymongo
import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import AgglomerativeClustering

col_name = 'product_simplified'
field_name = 'packaging'

input_limit = 5000
n_cluster = 600

n_cluster_start = 100
n_cluster_stop = 900
n_cluster_step = 50

output_field = 'product_name'

def pairwise_jaccard(X):
    return squareform(pdist(X, metric='jaccard'))

def pool_tags(tags, axis=1):
    dist = pairwise_jaccard(tags)
    dist_sum = np.sum(dist, axis=0)
    return tags[np.argmin(dist_sum)]

def cluster_radius(tags):
    dist = pairwise_jaccard(tags)
    dist_sum = np.sum(dist, axis=0)
    dist_avg = np.average(dist, axis=0)
    return dist_avg[np.argmin(dist_sum)]

def cluster_density(tags):
    radius = cluster_radius(tags)
    if radius <= 0:
        return 0
    return len(tags) / radius**2

def get_tag_idx_dict(db):
    cur = db.get_collection(field_name + "_idx").find()

    tag_idx = {}
    max_tag = 0
    for data in cur:
        tag_idx[data['_id']] = int(data['idx'])
        max_tag = max(max_tag, int(data['idx']))

    return tag_idx, max_tag

def get_data(db, max_tag):
    cur = db.get_collection(col_name).find(
        {field_name + '.0': {'$exists': True}}
    ).limit(input_limit)

    ids = []
    tags = []
    tag_names = []
    for data in cur:
        ids.append(data[output_field])
        tagIdxs = np.zeros(max_tag + 1)
        for tag in data[field_name]:
            if tag in tag_idx:
                tagIdxs[tag_idx[tag]] = 1
        tags.append(tagIdxs)
        tag_names.append(data[field_name])
    
    return ids, tags, tag_names

def cluster_tags(tags, n_cluster, full):
    clustering = AgglomerativeClustering(
        affinity=pairwise_jaccard, 
        pooling_func=pool_tags, 
        linkage='complete', 
        compute_full_tree=full,
        memory='cluster_cache/',
        n_clusters=n_cluster)
    return clustering.fit(np.vstack(tags))

def find_optimal_n_cluster(tags):
    for n_cluster in range(n_cluster_start, n_cluster_stop, n_cluster_step):    
        cluster = cluster_tags(tags, n_cluster, True)
        labels = cluster.labels_

        clusters = {}
        for i in range(len(tags)):
            if not labels[i] in clusters:
                clusters[labels[i]] = []
            clusters[labels[i]].append(tags[i])

        cluster_densities = []
        for i in clusters:
            cluster_densities.append(cluster_density(np.vstack(clusters[i])))
        print n_cluster, ':', np.min(cluster_densities), np.average(cluster_densities), np.max(cluster_densities)    

def get_clustering(tags, ids, n_cluster):
    cluster = cluster_tags(tags, n_cluster, False)
    labels = cluster.labels_

    clusters = {}
    for i in range(len(tags)):
        if not labels[i] in clusters:
            clusters[labels[i]] = []
        clusters[labels[i]].append(ids[i])    
    
    for i in clusters:
        print 'i:', clusters[i], '\n'

if __name__ == "__main__":
    db = pymongo.MongoClient().off

    tag_idx, max_tag = get_tag_idx_dict(db)
    ids, tags, tag_names = get_data(db, max_tag)

    #find_optimal_n_cluster(tags)
    get_clustering(tags, ids, n_cluster)

#5000 points
#n_cluster: min_density avg_density max_density
#100 : 0.0 6500.06074191 218772.792008
#150 : 0.0 10820.3659892 390446.44898
#200 : 0.0 61221.7208238 7200252.73469
#250 : 0.0 62274.1109766 7200252.73469
#300 : 0.0 67873.0152621 7200252.73469
#350 : 0.0 188130.748153 21743093.25
#400 : 0.0 168847.228109 21743093.25
#450 : 0.0 241283.077076 43441281.0
#500 : 0.0 296262.534177 43441281.0
#550 : 0.0 284255.623342 43441281.0
#600 : 0.0 276323.475954 43441281.0
#650 : 0.0 137471.714788 30375000.0
#700 : 0.0 39063.3372443 9725425.0
#750 : 0.0 30113.6955278 9725425.0
#800 : 0.0 26232.374219 9725425.0
#850 : 0.0 8754.02482051 4804839.0