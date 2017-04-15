from __future__ import division
from os.path import exists, isfile
from bson.son import SON
from pymongo import MongoClient
from collections import Counter

client = MongoClient()
db = client["off"]
products = db["products"]


pipeline = [
    { "$match": {"brands": {"$ne": None}}},
    { "$group": {"_id": "$brands", "count": {"$sum": 1}}},
    { "$sort": SON([("count", -1)])}
]

for x in list(products.aggregate(pipeline))[:20]:
    print("{}: {}".format(x["_id"], x["count"]))


predicted_grades = {}
PREDICTED_GRADES = "predicted_nutrition_grades.txt"
if exists(PREDICTED_GRADES) and isfile(PREDICTED_GRADES):
    print("Extracting predicted nutrition grades from file")
    with open(PREDICTED_GRADES, "r") as f:
        for line in f:
            _id,g = line.strip().split(", ")
            predicted_grades[_id] = g

# find products with required informations
pds = products.find(
        {
            "ingredients": {"$exists": True}, # use for prediction if nutrition grade does not exist
            "nutriments": {"$exists": True},
            "brands": {"$exists": True},
            "additives_tags": {"$exists": True},
            #"packaging_tags": {"$exists": True},
        },
        {
            "_id": 1,
            "nutrition_grades": 1,
            "nutriments": 1,
            "brands": 1,
            "additives_tags": 1,
            #"packaging_tags": 1,
        }
)

pds = list(pds) # store into memory
print("Matching count: {}".format(len(pds)))

score = {"a": 5, "b": 4, "c": 3, "d": 2, "e": 1}
useful_products = []
for pd in pds:
    if pd["brands"] == "":
        continue
    if not pd.has_key("nutrition_grades"):
        try:
            pd["nutrition_grades"] = predicted_grades[pd["_id"]]
        except:
            continue
    pd["grade_score"] = score[pd["nutrition_grades"]]
    useful_products.append(pd)
print("Useful count: {}".format(len(useful_products)))

brands = [pd["brands"] for pd in useful_products]
brands_count = Counter(brands)

# initialize results for top 20 brands (in terms of total records) for quick study
top_brands = []
results = {}
for brand,v in brands_count.most_common(20):
    top_brands.append(brand)
    results[brand] = {"t_sugars_100g": 0, "t_salt_100g": 0, "t_additives_count": 0, "t_grade_score": 0}

for pd in useful_products:
    if pd["brands"] in top_brands:
        try:
            results[pd["brands"]]["t_sugars_100g"] += pd["nutriments"]["sugars_100g"]
        except:
            pass
        try:
            results[pd["brands"]]["t_salt_100g"] += pd["nutriments"]["salt_100g"]
        except:
            pass
        try:
            results[pd["brands"]]["t_additives_count"] += len(pd["additives_tags"])
        except:
            pass
        results[pd["brands"]]["t_grade_score"] += pd["grade_score"]

print("<brand>: <average_sugars>, <average_salt>, <average_no_additives>, <average_grade>")
for brand,r in results.items():
    count = brands_count[brand]
    print("{:20}: {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}".format(
        brand,
        r["t_sugars_100g"] / count,
        r["t_salt_100g"] / count,
        r["t_additives_count"] / count,
        r["t_grade_score"] / count,
    ))

