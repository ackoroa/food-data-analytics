# -*- coding: utf-8 -*-
import re, itertools

processed_ingredient_names = []

with open('ingredients_temp.txt', 'r') as f:

	counter = 0

	for line in f:
		# if counter > 200:
		# 	break
		line = line.strip()

		if not line.startswith('"') or not line.endswith('",'):
			continue

		ingredient_name = line[1: -2]

		ingredient_names = re.findall('(\d+ ?(.?g|.?l)?|\D+ ?(.?g|.?l)?)', ingredient_name)
		ingredient_names = list(itertools.chain.from_iterable(ingredient_names))
		ingredient_names = [x.strip() for x in ingredient_names if (len(x) > 2 and not re.search(r'\d', x))]
		
		processed_ingredient_names.extend(ingredient_names)

	print 'Processing done.'

with open('ingredients_processed.txt', 'w+') as f:
	processed_ingredient_names = set(processed_ingredient_names)
	f.write('\n'.join(processed_ingredient_names))
	print 'saved.'