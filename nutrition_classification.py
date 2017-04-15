import json
import numpy as np
from bson.code import Code
from os.path import isfile, exists
from pymongo import MongoClient
from collections import Counter
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
predicted_labels = []

acceptable_grades = ["a", "b", "c", "d", "e"]
ingredients = "ingredients_tags"
grade = "nutrition_grades"
for p in products.find():
    if p.has_key(ingredients) and len(p[ingredients]) > 0:
        ingredients_str = " ".join(p[ingredients])
        if p.has_key(grade) and p[grade] in acceptable_grades:
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

RESULT_FILE = "predicted_nutrition_grades.txt"
if exists(RESULT_FILE) and isfile(RESULT_FILE):
    print("Extracting predicted results from file")
    with open(RESULT_FILE, "r") as f:
        for line in f:
            predicted_labels.append(line.strip().split(", ")[1])
    assert len(predicted_labels) == len(test_id)
else:
    vectorizer = CountVectorizer(analyzer="word", max_features=5000)
    train_features = vectorizer.fit_transform(train_dataset)
    np.asarray(train_features)

    print("Training classifier using Random Forest (will take around 30 minutes)")
    forest = RandomForestClassifier(n_estimators = 100)
    forest = forest.fit(train_features, train_labels)

    test_features = vectorizer.transform(test_dataset)
    np.asarray(test_features)

    print("Predicting missing nutrition grade information")
    predicted_labels = forest.predict(test_features)

    with open(RESULT_FILE, "w") as f:
        for i in range(len(test_id)):
            f.write("{}, {}\n".format(test_id[i], predicted_labels[i]))

print("Original grade distributions:")
for dist in Counter(train_labels).items():
    print("Grade {}: {}".format(*dist))

print("Predicted grade distributions:")
for dist in Counter(predicted_labels).items():
    print("Grade {}: {}".format(*dist))

print("New grade distributions:")
for dist in Counter(train_labels + predicted_labels).items():
    print("Grade {}: {}".format(*dist))
