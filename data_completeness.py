
CONNECTION_STRING = "mongodb://localhost:27017"
DATABASE_NAME = "off"
COLLECTION_NAME = "products"

from pymongo import MongoClient
from bson.code import Code
#import pymongo
#import json
#from sklearn.feature_extraction.text import CountVectorizer
#from apriori import runApriori, printResults

client = MongoClient(CONNECTION_STRING)
db = client[DATABASE_NAME]
openfood = db[COLLECTION_NAME]


mapper = Code("""
    function () {
        if (typeof this.states_tags !== "undefined"){
            for (var i = 0; i < this.states_tags.length; i++){
                emit(this.states_tags[i], 1);
            }
        }
    }""")

reducer = Code("""
    function (key, values) {
        var sum = 0;
        for(var i = 0; i < values.length; i++){
            sum += values[i];
        }
        return sum;
    }""")


completeness_stats = openfood.inline_map_reduce(mapper, reducer)

stats = {}
for x in completeness_stats:
    stats[x['_id']] = x['value']
    print("{}: {}".format(x['_id'],x['value']))

def completeness(state):
    completed_label = "en:"+state+"-completed"
    notcompleted_label = "en:"+state+"-to-be-completed"
    return 100.0 * stats[completed_label]/(stats[completed_label]+stats[notcompleted_label])

for state in ["brands", "categories", "ingredients", "nutrition-facts", "packaging"]:
    print("{:20}: {:.2f}%".format(state, completeness(state)))
