
# coding: utf-8

# # Configuration

# In[1]:

CONNECTION_STRING = "mongodb://localhost:27017"
DATABASE_NAME = "off"
COLLECTION_NAME = "products"


# # MongDB connection

# In[2]:

from pymongo import MongoClient
from bson.code import Code
import plotly, pymongo
plotly.offline.init_notebook_mode()
from plotly.graph_objs import Bar

client = MongoClient(CONNECTION_STRING)
db = client[DATABASE_NAME]
openfood = db[COLLECTION_NAME]


# # Nutrition grade

# In[6]:

mapper = Code("""
    function () {
        if (typeof this.nutrition_grades !== 'undefined' && this.nutrition_grades !== ""){
            emit(this.nutrition_grades, 1);
        }
    }""")
reducer = Code("""
    function (key, values) {
        var total = 0;
        for (var i = 0; i < values.length; i++) {
            total += values[i];
        }
        return total;
    }""")

grades = openfood.inline_map_reduce(mapper, reducer)
print grades


# In[14]:

import numpy as np
import matplotlib.pyplot as plt
 
objects = [item['_id'] for item in grades] # [a,b,c,d,e]
y_pos = np.arange(len(objects))
count = [item['value'] for item in grades]
 
plt.bar(y_pos, count, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Count')
plt.title('Nutrition Grades')
 
plt.show()


# Each food entry states the countries which the food it is sold. Below, we try to find out the list of countries which the food are sold.

# # Nutrients (100g)

# In[16]:

mapper = Code("""
    function () {
        if (typeof this.nutriments !== 'undefined' && this.nutriments !== "") {
            for (var key in this.nutriments) {
                if (key.match(/.*100g/))
                    emit(key, null);
            }
        }
    }""")
reducer = Code("""
    function (key, values) {
        return key
    }""")

nutriments_100g_fields = openfood.inline_map_reduce(mapper, reducer)
for n in nutriments_100g_fields:
    print n


# In[17]:

for n in nutriments_100g_fields:
    print n['_id']


# # Additives

# In[24]:

mapper = Code("""
    function () {
        if (typeof this.additives !== "undefined" && this.additives_n >= 0){
            var add = this.additives.substring(3, this.additives.length-3); // remove "^ [ " and " ] $"
            var add_str = add.split("  ]  [ ");
            for (var i = 0; i < add_str.length; i++){
                var additive_parts = add_str[i].split("  -> exists  -- ");
                if (additive_parts.length == 2){
                    var add_code = additive_parts[0].split(" -> ")[1];
                    emit(add_code, 1);
                }
            }
        }
    }""")
reducer = Code("""
    function (key, values) {
        var total = 0;
        for (var i = 0; i < values.length; i++) {
            total += values[i];
        }
        return total;
    }""")

additives_stats = openfood.inline_map_reduce(mapper, reducer)
print additives_stats


# In[29]:

add_clean = [(x['value'], x['_id']) for x in additives_stats]
add_clean.sort()

print len(add_clean)
for add in add_clean:
    print "{}: {}".format(add[0], add[1])

