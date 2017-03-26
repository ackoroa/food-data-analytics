import pymongo
import string

if __name__ == "__main__":
    db = pymongo.MongoClient().off
    count = db.products.count({'packaging_tags_en.0': {'$exists': True}})
    cur = db.products.find(
        {'packaging_tags_en.0': {'$exists': True}}, 
        {'_id': 1, 'packaging_tags_en': 1})

    i = 0
    for data in cur:
        tags = []
        for tag in data['packaging_tags_en']:
            for tag in tag.lower().split('-'):
                tags += tag.split()        

        cleanTags = []
        for tag in tags:
            tag = filter(lambda c: c not in string.punctuation + string.digits, tag)
            if tag.endswith('s') and not tag.endswith('ss'):
                tag = tag[:-1]
            if tag.endswith('es'):
                tag = tag[:-2]

            if tag == 'canning' or tag == 'canned' or tag == 'pot' or tag == 'cop':
                tag = 'can'
            if tag == 'plsatique' or tag == 'plastiktute' or tag == 'plastique' or tag == 'palstique' or tag == 'plastiqeu' or tag == 'plastiqe' or tag == 'plastque' or tag == 'platique' or tag == 'plastc' or tag == 'plastico' or tag == 'platic':
                tag = 'plastic'
            if tag == 'aluminum' or tag == 'alluminum' or tag == 'alu' or tag == 'alimunium' or tag == 'alluminium' or tag == 'aluminiumn' or tag == 'alumium' or tag == 'aluminise' or tag == 'aluminized' or tag == 'aluminiumbeutel' or tag == 'aluminiumblikken' or tag == 'aluminiumburk' or tag == 'alumina' or tag == 'aluminee' or tag == 'alumminium':
                tag = 'aluminium'
            if tag == 'barquette':
                tag = 'tray'
            if tag == 'opercule' or tag == 'opecule':
                tag = 'operculum'
            if tag == 'bouteille' or tag == 'bottled' :
                tag = 'bottle'
            if tag == 'etui':
                tag = 'case'
            if tag == 'couvercle':
                tag = 'lid'
            if tag == 'papier':
                tag = 'paper'
            if tag == 'verre':
                tag = 'glass'
            if tag == 'feuille':
                tag = 'foil'
            if tag == 'cartonnette' or tag == 'caton':
                tag = 'carton'
            if tag == 'metallic':
                tag = 'metal'
    
            if len(tag) > 2:
                cleanTags.append(tag)

        db.products.update_one(
            {'_id':data['_id']}, 
            {'$set': {'packaging_clean': list(set(cleanTags))}}, 
            upsert=False)

        i += 1
        if i % 50 == 0:
            print i, "/", count
    print i, "/", count
    print "Completed"
