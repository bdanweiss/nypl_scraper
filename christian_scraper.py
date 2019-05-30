#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
import time
import sys
import string
import enchant

# Search parameters
begin_date = "01/01/2014"
end_date =  "01/01/2019"
search_term = "christian"
publication = "New York Post"
negative_terms = ["violent", "violence", "radical", "fanatic", 
				"fundamentalis", "terror", "terrorist", "terrorism", 
				"jihad", "militant", "refugee", "extremis", 
				"murder", "barbaric", "barbarian"]

# Scraping/data parameters
wait_time = 30
file_name = "christian_search.csv"
driver = None
scrape_limit = 3000
browser_width = 900
browser_height = 800
dictionary = enchant.Dict("en_US")
grammar_articles = ["a", "the", "an", "those", 
			"these", "this", "his", "her"]
pesky_last_names = ["Louboutin", "Slater", "Dior", "Bale", 
					"Ponder", "Betancourt"]

# Clean the text of special characters, like tags, newlines, tabs, etc.
def clean_text(html_text):
    # Remove tags
    unicode_text = html_text.get_text()

    # Remove new lines, tabs, null characters, quadruple spaces, and the beginning "Full Text" thing
    kinda_clean_text = unicode_text.replace("\n", " ").replace("\t", " ").replace(chr(0), "").replace("    ", " ").replace("Full Text", "").replace("   ", "")

    # Remove punctuation
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space
    cleaner_text = kinda_clean_text.translate(translator)

    # Remove weird characters using regex
    cleanest_text = re.sub(r'/[^\w\s]/gi', ' ', cleaner_text)
    return cleanest_text

def pull_data_from_article(article_page):

	article = article_page.find_all("div", class_="document-text")[0]
	cleaned =  clean_text(article)
	title = article_page.find("span", id="docSummary-title").get_text()

	# If the article has christian as a name, move on. Otherwise, scrape the data
	if christian_is_name(cleaned):
		print ("skipped", title)
		return None
	else:
		cleaned = cleaned.lower()
		# Get the article text and title
		title = article_page.find("span", id="docSummary-title").get_text()
		url_data = article_page.find_all("span", class_="docUrl")[0].get_text()

		# First, find the heading of each article
		heading = article_page.find_all("span", class_="definition")[2].get_text()

		# Then, use regular expressions to get the date between the parentheses
		date = re.findall(r'\((.*?)\)', heading)[1].split(", ")

		# Finally, organize the one date string into year, month, and day
		year = date[1]
		month_day = date[0].split(" ")
		month = month_day[0].replace(" ", "").replace("\t", "").replace("\n", "")
		day = month_day[1]

		# Clean the article text and check for stuff.
		data_for_article = {'Title': title,
							'URL': url_data,
						    'Year': year,
						    'Month': month,
						    'Day': day
			 			   }
		term_used = False
		for word in negative_terms:
			if word in cleaned.lower():
				data_for_article[word] = True
				term_used = True
			else:
				data_for_article[word] = False

		data_for_article["Term Used"] = term_used
		return data_for_article

def christian_is_name(text):

	# Make a list of all the words
	word_list = text.split(" ")

	# For some reason, this list has empty characters. Remove them. Get rid of one letters too (except a and i).
	word_list = [word for word in word_list if not len(word) == 0]
	word_list = [word for word in word_list if not (len(word) == 1 and (word != "a" or word != "i"))]

	# Go through each word in the article and figure out if christian is a name or not.
	counter = 0
	list_length = len(word_list)
	strikes_list = []
	is_name = False

	for word in word_list:

		# Make sure we don't go outside the list	
		if counter != 0:
			before = word_list[counter - 1]
		else:
			before = "word"
		if counter != list_length - 1:
			after = word_list[counter + 1]
		else:
			after = "word"

		# Skip the aritcle if the word AFTER "christian" isn't in the dictionary.
		if word.lower() == "christian":
			if not dictionary.check(after.lower()):
				print (word, after)
				strikes_list.append(True)

			if not dictionary.check(before):
				print (before, word)
				strikes_list.append(True)

			if after in pesky_last_names:
				print (word, after)
				strikes_list.append(True)

			if before in grammar_articles:
				strikes_list.append(False)

		counter += 1

	# Basically, using christians as a plural probably means we're referring to a religion
	# Even if there's a name in the article, I'd still count it in an analysis
	if "Christians" in word_list:
		strikes_list.append(False)

	if True in strikes_list and False not in strikes_list:
		is_name = True

	elif False in strikes_list:
		is_name = False

	return is_name

def access_article_link(link):
	global driver

	# Get the URL and hand over to Beautiful Soup
	article_url = "https://go-galegroup-com.i.ezproxy.nypl.org/ps/" + link['href']

	driver.get(article_url)
	
	article_page = BeautifulSoup(driver.page_source, 'lxml')

	# Refresh until it works
	no_error = True
	while no_error:
		try:
			article = article_page.find_all("div", class_="document-text")[0]
			no_error = False
		except:
			driver.close()
			driver = webdriver.Chrome('./chromedriver')
			driver.implicitly_wait(wait_time)
			driver.get(article_url)
			login()
			article_page = BeautifulSoup(driver.page_source, 'lxml')
			no_error = True

	return pull_data_from_article(article_page)

def login():
	# Fill out form for user info and log into database
	driver.find_element_by_xpath("//input[@name='user']").send_keys('')
	driver.find_element_by_xpath("//input[@name='pass']").send_keys('')
	driver.find_element_by_xpath("//input[@type='submit']").click()

def main():	
	global driver

	# Get the webdriver and starting url
	url = "https://login.i.ezproxy.nypl.org/login?qurl=https%3a%2f%2finfotrac.galegroup.com%2fitweb%2fnypl%3fdb%3dSP01"
	driver = webdriver.Chrome('./chromedriver')
	driver.set_window_position(0, 0)
	driver.set_window_size(browser_width, browser_height)
	driver.implicitly_wait(wait_time)
	driver.get(url)

	# Fill out form for user info and log into database
	login()

	# Once in database, get to the publications section, 
	# click to get all publications and click on NY Post
	driver.find_element_by_id("searchType-publication").click()
	driver.find_element_by_id("publicationSearch_listAll").click()
	driver.find_element_by_xpath("//a[contains(text(), '"+ publication + "')]").click()

	# Type in search term and click on the search, get to the date range, and click/manipulate 
	# the custom range
	driver.find_element_by_id("quickSearchTerm").send_keys(search_term)
	driver.find_element_by_id("quickSearchSubmit").click()
	driver.find_element_by_xpath("//a[@title='Custom Date Range']").click()
	driver.find_element_by_id("beginDate").click()
	driver.find_element_by_id("beginDate").send_keys(begin_date)
	driver.find_element_by_id("endDate").click()
	driver.find_element_by_id("endDate").send_keys(end_date)
	driver.find_element_by_id("custom_limiter").click()

	# Sort the results by newest to oldest and then start clicking on the see more tab
	driver.find_element_by_id("sorter").click()
	driver.find_element_by_xpath("//option[@value='DA-SORT']").click()
	driver.find_element_by_id("searchResultsControls").click()

	# Keep on clicking on the "show more" button until we can't anymore.
	no_error = True
	while no_error:
		time.sleep(3)
		try:
			driver.find_element_by_id("searchResultsControls").click()
		except:
			no_error = False

	# Get all links to articles I'm checking and create an empty list for the data.
	html = BeautifulSoup(driver.page_source, 'lxml')
	links = html.find_all("a", class_="documentLink")
	total_articles = len(links)
	counter = 0
	skipped = 0
	data = []

	# Get data from each article
	for link in links:
		data_for_article = access_article_link(link)

		if counter == scrape_limit:
			break

		if data_for_article == None:
			skipped += 1
		else:
			data.append(data_for_article)

		counter += 1
		print("Skipped:", skipped, "Scraped:", counter, "Total:", total_articles)

	dataframe = pd.DataFrame(data)
	dataframe.to_csv(file_name, encoding='utf-8', index=False)

main()