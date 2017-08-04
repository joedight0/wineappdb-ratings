#!/bin/python3

import re #regular expressions
import requests
from bs4 import BeautifulSoup
import argparse
import sys

def ProcessGameName(game):
	#game = game.lower()
	game = game.replace("&","and")
	game = game.replace(".","")
	game = game.replace(" :",":")
	game = re.sub("\(.*\)","",game)
	game = game.replace("  "," ")
	game = game.strip()
	return game


def ExtractGameList(html):
	GameList = []
	soup = BeautifulSoup(html,"lxml")

	table = soup.find("table", { "class" : "whq-table whq-table-full" })
	for row in table.findAll("tr"):
		cells = row.findAll("td")
		#print("*********************")
		game = cells[0].findAll("a")[0].text
		game = ProcessGameName(game)
		GameList.append(game)
		
	GameList.pop(0)
	return GameList

def ExtractNumberOfPages(html):
	A = re.findall(".*Page <b>1</b> of <b>(.*)</b>.*",html)
	if (A):
		return int(A[0])
	return 0

def GetWineHqList(ratingsList):
	posturl = "https://appdb.winehq.org/objectManager.php"

	getparams = {
		"bIsQueue": "false",
		"bIsRejected": "false",
		"sClass": "application",
		"sTitle": "Browse+Applications",
		"iItemsPerPage": 200,
		"iPage": 1,
		"sOrderBy": "appName",
		"bAscending": "true"
		}

	postparams = {
		"iappVersion-ratingOp": "5", 
		"iappCategoryOp": "11", 
		"iappVersion-licenseOp": "5",
		"sappVersion-ratingData": "Platinum", 
		'iversions-idOp': '5',
		"sversions-idData": "",
		"sappCategoryData": "2", #Replace by "2"?
		"sappVersion-licenseData": "Retail", #Replace by retail
		'iappFamily-keywordsOp': '2',
		'sappFamily-keywordsData': "",
		'iappFamily-appNameOp': '2',
		'sappFamily-appNameData': "",
		"ionlyDownloadableOp": "10",
		"sonlyDownloadableData": "false"
		}

	#getpluspost = {**getparams,**postparams}
	getpluspost = dict(getparams)
	getpluspost.update(postparams)
	
	Games = {}
	for rating in RatingsList:
		Games[rating] = []
	
	for rating in RatingsList:
		getpluspost["iPage"] = 1
		getpluspost["sappVersion-ratingData"] = rating
			
		r = requests.post(posturl, data=getpluspost)
		html = r.text

		n = ExtractNumberOfPages(html)
		Games[rating] = ExtractGameList(html)
		
		for page in range(2,n+1):
			getpluspost["iPage"] = page
			r = requests.post(posturl, data=getpluspost)
			html = r.text
			Games[rating].extend(ExtractGameList(html))
	return Games

parser = argparse.ArgumentParser(description="Which ratings would you like to extract from winehq.org appdb?")
parser.add_argument('-p','--platinum', action="store_true", help='Extract games with a rating of Platinum')
parser.add_argument('-g','--gold', action="store_true", help='Extract games with a rating of Gold')
parser.add_argument('-s','--silver', action="store_true", help='Extract games with a rating of Silver')
parser.add_argument('-b','--bronze', action="store_true", help='Extract games with a rating of Bronze')
parser.add_argument('-x','--garbage', action="store_true", help='Extract games with a rating of Garbage')
parser.add_argument('-a','--all', action="store_true", help='Extract all games, to a single file')

args = parser.parse_args()

RatingsList = []

if (args.platinum):
	RatingsList.append("Platinum")
if (args.gold):
	RatingsList.append("Gold")
if (args.silver):
	RatingsList.append("Silver")
if (args.bronze):
	RatingsList.append("Bronze")
if (args.garbage):
	RatingsList.append("Garbage")
if (args.all):
	RatingsList.append("Platinum")
	RatingsList.append("Gold")
	RatingsList.append("Silver")
	RatingsList.append("Bronze")
	RatingsList.append("Garbage")

if (not RatingsList):
	print("You must specify at least one of [-p][-g][-s][-b][-x][-a]")
	sys.exit(0)


Games = GetWineHqList(RatingsList)
if (not args.all):
	numratings = len(RatingsList)
	for rating in RatingsList:
		if (numratings > 1):
			print("# Games with rating", rating)
		for game in Games[rating]:
			if (numratings > 1):
				print("\t",game)
			else:
				print(game)
else:
	for rating in Games:
		for game in Games[rating]:
			print("\t",game,"\tIS\t",rating)
