from __future__ import division
from pymongo import MongoClient
from bson.code import Code
from apriori import runApriori, printResults

client = MongoClient()
db = client["off"]
products = db["products"]

product_ingredients = []
total_ingredients = 0


for p in products.find():
    key = "ingredients_tags"
    if p.has_key(key) and len(p[key]) > 0:
        product_ingredients.append(p[key])
        total_ingredients += len(p[key])

print("Total products with ingredients: {}".format(len(product_ingredients)))
print("Total number of recorded ingredients: {}".format(total_ingredients))
print("Average number of ingredients per product: {}".format(len(product_ingredients)/total_ingredients))

minSupport = 0.2
minConfidence = 0.7
items, rules = runApriori(product_ingredients, minSupport, minConfidence)
printResults(items, rules)

