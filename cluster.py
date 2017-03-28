import pymongo
import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import AgglomerativeClustering

col_name = 'product_simplified'
field_name = 'ingredients'
input_limit = 100
n_cluster = 10

def pairwise_jaccard(X):
    return squareform(pdist(X, metric='jaccard'))

def pool_tags(tags, axis=1):
    dist = pairwise_jaccard(tags)
    dist_sum = np.sum(dist, axis=0)
    return tags[np.argmin(dist_sum)]

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
        ids.append(data['product_name'])
        tagIdxs = np.zeros(max_tag + 1)
        for tag in data[field_name]:
            tagIdxs[tag_idx[tag]] = 1
        tags.append(tagIdxs)
        tag_names.append(data[field_name])
    
    return ids, tags, tag_names

if __name__ == "__main__":
    db = pymongo.MongoClient().off

    tag_idx, max_tag = get_tag_idx_dict(db)
    ids, tags, tag_names = get_data(db, max_tag)
    
    clustering = AgglomerativeClustering(affinity=pairwise_jaccard, pooling_func=pool_tags, linkage='complete', n_clusters=n_cluster)
    labels = clustering.fit_predict(np.vstack(tags))
    
    clusters = {}
    for i in range(len(ids)):
        if not labels[i] in clusters:
            clusters[labels[i]] = []
        clusters[labels[i]].append(ids[i])

    for i in clusters:
        print i, ':', clusters[i], '\n'
