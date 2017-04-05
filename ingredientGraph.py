import pymongo
import networkx as nx
import matplotlib.pyplot as plt

if __name__ == "__main__":
    db = pymongo.MongoClient().off

    cur = db.product_simplified.find(
        {'ingredients.0': {'$exists': True}}
    ).limit(1000000)

    G = nx.Graph()
    for data in cur:
        ingredients = data['ingredients']
        for i in range(len(ingredients)):
            for j in range(i + 1, len(ingredients)):
                u = ingredients[i]
                if u == 'cell': u = 'salt'
                v = ingredients[j]
                if v == 'cell': v = 'salt'

                if u == 'water' or u == 'salt' or u == 'sugar' or v == 'water' or v == 'salt' or v == 'sugar':
                    continue

                w = G.get_edge_data(u, v, default={'weight':0})['weight']
                G.add_edge(u, v, {'weight':w + 1})

    G.remove_edges_from([(u,v) for u,v,attr in G.edges(data=True) if attr['weight'] < 800])
    G.remove_nodes_from([node for node,degree in G.degree().items() if degree < 1])
    print G.nodes()
    
    pos = nx.spring_layout(G, k=0.25, weight=None)
    nx.draw_networkx_edges(G, pos, alpha=0.03)
    nx.draw_networkx_labels(G, pos)
    plt.show()