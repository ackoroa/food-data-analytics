import json
import numpy as np
from bson.code import Code
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier

client = MongoClient()
db = client["off"]
products = db["products"]

train_id = [] # product "_id"
train_dataset = [] # ingredients of products with grade labels
train_labels = [] # grade labels for products in ordered manner
test_id = [] # product "_id"
test_dataset = [] # ingredients of products without grade labels

grades = ["a", "b", "c", "d", "e"]
ingredients = "ingredients_tags"
grade = "nutrition_grades"
for p in products.find():
    if p.has_key(ingredients) and len(p[ingredients]) > 0:
        ingredients_str = " ".join(p[ingredients])
        if p.has_key(grade) and p[grade] in grades:
            train_dataset.append(ingredients_str)
            train_labels.append(p[grade])
            train_id.append(p["_id"])
        else:
            test_dataset.append(ingredients_str)
            test_id.append(p["_id"])

print("Total products with grades: {}".format(len(train_dataset)))
print("Total products without grades: {}".format(len(test_dataset)))
assert len(train_id) == len(train_dataset) == len(train_labels)
assert len(test_id) == len(test_dataset)

vectorizer = CountVectorizer(analyzer="word", max_features=5000)
train_features = vectorizer.fit_transform(train_dataset)
np.asarray(train_features)

print("Training classifier using Random Forest (will take around 30 minutes)")
forest = RandomForestClassifier(n_estimators = 100)
forest = forest.fit(train_features, train_labels)

test_features = vectorizer.transform(test_dataset)
np.asarray(test_features)

print("Predicting missing nutrition grade information")
grades = forest.predict(test_features)

with open("predicted_nutrition_grades.txt", "w") as f:
    for i in range(len(test_id)):
        f.write("{}, {}\n".format(test_id[i], grades[i]))

