import json
import numpy as np
from bson.code import Code
from os.path import isfile, exists
from pymongo import MongoClient
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

client = MongoClient()
db = client["off"]
products = db["products"]

dataset = [] # ingredients of products with grade labels
labels = [] # grade labels for products in ordered manner

acceptable_grades = ["a", "b", "c", "d", "e"]
ingredients = "ingredients_tags"
grade = "nutrition_grades"
for p in products.find():
    if p.has_key(ingredients) and len(p[ingredients]) > 0:
        ingredients_str = " ".join(p[ingredients])
        if p.has_key(grade) and p[grade] in acceptable_grades:
            dataset.append(ingredients_str)
            labels.append(p[grade])


print("Total products with grades: {}".format(len(dataset)))
assert len(dataset) == len(labels)

offset = int(0.8 * len(dataset))

vectorizer = CountVectorizer(analyzer="word", max_features=5000)
train_features = vectorizer.fit_transform(dataset[:offset])
np.asarray(train_features)

print("Training classifier using Random Forest (will take around 30 minutes)")
forest = RandomForestClassifier(n_estimators = 100)
forest = forest.fit(train_features, labels[:offset])

test_features = vectorizer.transform(dataset[offset:])
np.asarray(test_features)
predicted = forest.predict(test_features)

score = metrics.accuracy_score(labels[offset:], predicted)
print("Accuracy score: {:.2f}%".format(score*100))
