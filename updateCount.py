from pymongo import MongoClient
import re, itertools

split_pattern = re.compile('(?P<ingredient_name>.+) ?(\d+ |\d+ ?.?g|\d+ ?ml)*')

mongo = MongoClient()
count = 0

translation_dict = {}

def load_dict():
	with open('ingredients_translated.txt', 'r') as dict_f:
		for line in dict_f:
			values = line.strip().split('\t')
			if len(values) != 2:
				print "???", values
			translation_dict[values[0]] = values[1]

	print "Dictionary loaded. Length:", len(translation_dict)

def lookup(text):
	if (text in translation_dict):
		return translation_dict[text].lower()
	else:
		return text


if __name__ == '__main__':

	load_dict()

	count = 0

	for ingredient in mongo.off.ingredientCount.find():
		count += 1
		ingredient_name = ingredient['_id'].replace('-',' ')
		ingredients = re.findall('(\d+ ?(.?g|.?l)?|\D+ ?(.?g|.?l)?)', ingredient_name)
		ingredients = list(itertools.chain.from_iterable(ingredients))
		ingredients = [x.strip() for x in ingredients if (len(x) > 2 and not re.search(r'\d', x))]

		if count%1000 == 0:
			print "Processed", count

		if len(ingredients) > 0:
			# print ingredient['_id'], ', '.join(ingredients)
			for ingredient_split in ingredients:
				translated_food_name = lookup(ingredient_split)
				if len(translated_food_name) < 1: continue
				mongo.off.ingredientTranslated.insert_one({'name': translated_food_name, 'count': ingredient['value']})

