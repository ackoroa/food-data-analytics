import pymongo
import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import AgglomerativeClustering

col_name = 'brand_ingredients_trunc'
field_name = 'ingredients'

input_limit = 100
n_cluster = 35

n_cluster_start = 10
n_cluster_stop = 60
n_cluster_step = 5

output_field = '_id'

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

def get_clustering(tags, tag_names, ids, n_cluster):
    cluster = cluster_tags(tags, n_cluster, False)
    labels = cluster.labels_

    clusters = {}
    clusters_ids = {}
    for i in range(len(tags)):
        if not labels[i] in clusters:
            clusters[labels[i]] = []
            clusters_ids[labels[i]] = []
        clusters[labels[i]].append(tags[i])
        clusters_ids[labels[i]].append(ids[i])
    
    f = open('clusters.out', 'w')
    for i in clusters:
        clustroid = pool_tags(np.vstack(clusters[i]))
        clustroid_idx = [np.array_equal(clustroid, tag) for tag in tags].index(True)
        #f.write(str(map(lambda tag_name: tag_name.encode('ascii', 'ignore'), tag_names[clustroid_idx])))
        #f.write(':\n')
        for name in clusters_ids[i]:
            f.write(name.encode('ascii', 'ignore') + '\n')
        f.write('\n')

def find_optimal_n_cluster(tags):
    print 'n_cluster: min average max (cluster_radius)'
    for n_cluster in range(n_cluster_start, n_cluster_stop + 1, n_cluster_step):    
        cluster = cluster_tags(tags, n_cluster, True)
        labels = cluster.labels_

        clusters = {}
        for i in range(len(tags)):
            if not labels[i] in clusters:
                clusters[labels[i]] = []
            clusters[labels[i]].append(tags[i])

        cluster_radiuses = []
        for i in clusters:
            cluster_radiuses.append(cluster_radius(np.vstack(clusters[i])))
        print n_cluster, ':', np.min(cluster_radiuses), np.average(cluster_radiuses), np.max(cluster_radiuses)    

if __name__ == "__main__":
    db = pymongo.MongoClient().off

    tag_idx, max_tag = get_tag_idx_dict(db)
    ids, tags, tag_names = get_data(db, max_tag)

    #find_optimal_n_cluster(tags)
    get_clustering(tags, tag_names, ids, n_cluster)
