
CONNECTION_STRING = "mongodb://localhost:27017"
DATABASE_NAME = "off"
COLLECTION_NAME = "products"

from pymongo import MongoClient
from bson.code import Code
import pymongo
import json
from sklearn.feature_extraction.text import CountVectorizer
from apriori import runApriori, printResults

client = MongoClient(CONNECTION_STRING)
db = client[DATABASE_NAME]
openfood = db[COLLECTION_NAME]


mapper = Code("""
    function () {
        if (typeof this.additives !== "undefined" && this.additives_n >= 0){
            var add = this.additives.substring(3, this.additives.length-3); // remove "^ [ " and " ] $"
            var add_str = add.split("  ]  [ ");
            for (var i = 0; i < add_str.length; i++){
                var additive_parts = add_str[i].split("  -> exists  -- ");
                if (additive_parts.length == 2){
                    var add_code = additive_parts[0].split(" -> ")[1];
                    emit(this._id, add_code);
                }
            }
        }
    }""")

reducer = Code("""
    function (key, values) {
        return values.join("_");
    }""")


DATASET_FILENAME = "dataset-product_id-additives.json"
try:
    additives_stats = json.load(open(DATASET_FILENAME, "r"))
    print("Using processed dataset")
except:
    print("Building dataset")
    additives_stats = openfood.inline_map_reduce(mapper, reducer)
    json.dump(additives_stats, open(DATASET_FILENAME, "w"))

#add_clean = [(x['_id'], x['value'].split("_")) for x in additives_stats]
#add_clean.sort()
#for add in add_clean:
#    print("{}: {}".format(add[0], add[1]))

ordered_ids = [ x['_id'] for x in additives_stats ]
ordered_additives = [ x['value'] for x in additives_stats ]

vectorizer = CountVectorizer(tokenizer=lambda x: x.split("_"), binary=True)
X = vectorizer.fit_transform(ordered_additives)
Xarray = X.toarray()
print("Feature names: ", vectorizer.get_feature_names())
#print(dir(Xarray))
print("Feature vector size: ", Xarray.size)
print("Feature vector shape: ", Xarray.shape)
print("Number of samples: ", len(ordered_additives))
#print(type(Xarray))

ordered_additives_split = [ x['value'].split("_") for x in additives_stats ]

minSupport = 0.03
minConfidence = 0.7
items, rules = runApriori(ordered_additives_split, minSupport, minConfidence)
printResults(items, rules)

