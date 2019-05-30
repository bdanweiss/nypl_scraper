import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.font_manager as font_manager
import matplotlib.ticker as mtick
import numpy as np

def combine_counts(column1, column2, dataframe):
	count = 0
	for index, row in dataframe.iterrows():
		if row[column1] == True and row[column2] == True:
			count += 1
		elif row[column1] == True:
			count += 1
		elif row[column2] == True:
			count += 1
	return count

def get_count(column, dataframe):
	count = 0
	for index, row in dataframe.iterrows():
		if row[column] == True:
			count += 1
	return count

def main():
	christian_data = pd.read_csv("christian_search.csv") 
	muslim_data = pd.read_csv("muslim_search.csv") 

	row_count_muslim = muslim_data.shape[0]
	row_count_christian = christian_data.shape[0]

	column_count = muslim_data.shape[1]

	counter = 0
	muslim_tuple_list = []
	avoid_list = ["barbarian", "barbaric",  "terrorist", "terrorism", "violent", "violence"]

	for column in muslim_data:
		if counter > 5 and column not in avoid_list:
			muslim_percentage = round((get_count(column, muslim_data)/row_count_muslim), 4)
			muslim_tuple_list.append((column, muslim_percentage*100))
			print(column, muslim_percentage)

		counter += 1

	barbarian_percentage = round((combine_counts("barbarian", "barbaric", muslim_data)/row_count_muslim), 4)
	violence_percentage = round((combine_counts("violent", "violence", muslim_data)/row_count_muslim), 4)
	print("barbarian", barbarian_percentage)
	print("violence", violence_percentage)

	muslim_tuple_list.append(("barbarian", barbarian_percentage*100))
	muslim_tuple_list.append(("violence", violence_percentage*100))

	muslim_tuple_list = sorted(muslim_tuple_list, key=lambda x: x[1], reverse=True)

	words = []
	muslim_hits = []
	christian_hits = []

	print("--------------------")

	indices = 0
	for item in muslim_tuple_list:
		indices += 1
		word = item[0]
		muslim_hits.append(item[1])
		if word == "barbarian":
			christian_percentage = round((combine_counts("barbaric", "barbarian", christian_data)/row_count_christian), 4)
		elif word == "violence":
			christian_percentage = round((combine_counts("violent", "violence", christian_data)/row_count_christian), 4)
		else:
			christian_percentage = round((get_count(word, christian_data)/row_count_christian), 4)
		print(word, christian_percentage)

		christian_hits.append(christian_percentage*100)

		if word == "fundamentalis":
			word = "fundamentalism"
		elif word == "extremis":
			word = "extremism"
		words.append(word)

	bar_width = .35       
	r1 = np.arange(indices)
	r2 = [x + bar_width for x in r1]
	fig, ax = plt.subplots()
	p1 = ax.barh(r1, muslim_hits, bar_width, label="Muslim")
	p2 = ax.barh(r2, christian_hits, bar_width, label='Christian')

	font = font_manager.FontProperties(family='Arial',
	                                   style='normal', size=10)

	plt.legend(loc='best', frameon=False, prop=font)
	plt.gca().xaxis.set_major_formatter(PercentFormatter(1))
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.spines['left'].set_visible(False)
	plt.yticks([r + bar_width for r in range(len(words))], words)
	ax.tick_params(axis='y', which='both', length=0)

	fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
	xticks = mtick.FormatStrFormatter(fmt)
	ax.xaxis.set_major_formatter(xticks)
	plt.xticks(np.arange(0, 50, 5))

	for tick in ax.get_xticklabels():
	    tick.set_fontname("Arial")

	for tick in ax.get_yticklabels():
	    tick.set_fontname("Arial")

	plt.show()

main()