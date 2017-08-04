#!/bin/python3

import re #regular expressions
import subprocess
import os
import sys
Games = {} #empty dictionary

def Canonicalize(s):
	S = s.lower()
	S = S.strip()
	S = S.replace('\'',"")
	S = S.replace('-',"")
	S = S.replace(':',"")
	S = S.replace('+',"")
	S = S.replace('=',"")
	S = S.replace("  "," ")
	S = S.replace("!","")
	S = S.replace("?","")
	return S


print("Getting WineDB list... ",)
if (not os.path.isfile("winedb.txt")):
	os.system(sys.executable + " winehqextract.py -a > winedb.txt")
	print("\tDone!")
else:
	print("\tUsing existing list.")

with open("winedb.txt", 'r') as file:
		games = file.read().split("\n")
		for game in games:
			if len(game):
				print(game.split("\tIS\t"))
				Games[Canonicalize(game.split("\tIS\t")[0])] = Canonicalize(game.split("\tIS\t")[1])
			
print("Getting list of your steam games... ",)
if (not os.path.isfile("steamgames.txt")):
	os.system(sys.executable + " steamextract.py MySteamGames.html > steamgames.txt")
	print("\tDone!")
else:
	print("\tUsing already found file! If you wish to recover again, rename or delete steamgames.txt")



# dict of games
mygames = {}
distribution = {
	"garbage" : 0,
	"bronze" : 0,
	"silver" : 0,
	"gold" : 0,
	"platinum" : 0
	}
numGames = 0
numwine = 0

colours = {
	"garbage" : "\033[31m",
	"bronze"  : "\033[33m",
	"silver"  : "\033[33m",
	"gold"    : "\033[32m",
	"platinum": "\033[32m"
    }

with open("steamgames.txt", 'r') as myfile:
		txt = myfile.read()
		steams = txt.split("\n")
		numGames = len(steams)
		for game in steams:
			if (not game):
				continue
			cg = Canonicalize(game)
			if (cg in Games):
				print("\t{}{} ...  {}\033[0m".format(colours[Games[cg]], game, Games[cg].title()))
				numwine += 1
				distribution[Games[cg]] += 1
				mygames[game] = Games[cg].title()
			else:
				print("\t{} ...  Not in database".format(game))
				mygames[game] = "Not in database"

# Write a list of games 
with open("results.tsv", 'w') as results:
		for k,v in mygames.items():
			results.write("{0}\t{1}\n".format(k,v))

numPlayable = distribution["gold"] + distribution["platinum"]
print("")
print("Finished!")
print("Out of {} games in you own, {} are on the database, and you could play {} games in wine!".format(numGames, numwine, numPlayable))
print("This is {}% of your entire library, or {}% of those found on wineDB.".format(round((numPlayable / numGames) * 100.0, 2), round((numPlayable / numwine) * 100.0, 2)))
print("{}% of your library was on wineDB.".format(round((numwine/numGames)*100.0, 2)))

print("Breakdown: ")
for rating in distribution.keys():
    #TODO: justify this list, key.
	print("{}{} : {} ({}%)\033[0m" .format(colours[rating], rating.title(), distribution[rating], round((distribution[rating] / numwine) * 100.0, 2)))
