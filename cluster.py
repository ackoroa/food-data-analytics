import pymongo
import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import AgglomerativeClustering

def pairwise_jaccard(X):
    return squareform(pdist(X, metric='jaccard'))

def pool_tags(tags, axis=1):
    dist = pairwise_jaccard(tags)
    dist_sum = np.sum(dist, axis=0)
    return tags[np.argmin(dist_sum)]

if __name__ == "__main__":
    db = pymongo.MongoClient().off
    cur = db.pack_idx.find()

    tag_idx = {}
    idx_tag = {}
    max_tag = 0
    for data in cur:
        tag_idx[data['pack_tag']] = int(data['idx'])
        idx_tag[int(data['idx'])] = data['pack_tag']
        max_tag = max(max_tag, int(data['idx']))

    cur = db.products.find(
        {'packaging_clean': {'$exists': True}}, 
        {'_id': 1, 'packaging_clean': 1, 'product_name': 1}
    ).limit(1000)

    ids = []
    tags = []
    tag_names = []
    for data in cur:
        ids.append(data['product_name'])
        tagIdxs = np.zeros(max_tag + 1)
        for tag in data['packaging_clean']:
            tagIdxs[tag_idx[tag]] = 1
        tags.append(tagIdxs)
        tag_names.append(data['packaging_clean'])
    
    clustering = AgglomerativeClustering(affinity=pairwise_jaccard, pooling_func=pool_tags, linkage='complete', n_clusters=20)
    labels = clustering.fit_predict(np.vstack(tags))
    
    clusters = {}
    for i in range(len(ids)):
        if not labels[i] in clusters:
            clusters[labels[i]] = []
        clusters[labels[i]].append(tag_names[i])

    for i in clusters:
        print i, ':', clusters[i], '\n'