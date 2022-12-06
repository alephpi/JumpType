import re
import json

name = 'prefix-suffix.txt'

with open(name, 'r', encoding='utf-8') as file:
	txt = file.read().strip()
txt = re.sub(r'[\n|,|/]',' ', txt)
txt = re.sub(r' +',' ', txt)
lst = txt.split(' ')

prefixes = []
suffixes = []
for token in lst:
	if token[0] == '-':
		suffixes.append(token)
	elif token[-1] == '-':
		prefixes.append(token)

with open('en_prefixes.json', 'w') as f:
	json.dump(prefixes, f)

with open('en_suffixes.json', 'w') as f:
	json.dump(suffixes, f)



