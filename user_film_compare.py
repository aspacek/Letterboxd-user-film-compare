import requests
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import csv

##
## Written by Alex Spacek
## March 2020 - April 2020
##

#########################
# The similarity systems:
#
# SYSTEM = 1
# Points are assigned based on difference in ratings,
# With 1 being completely different and 10 being exactly the same:
# Difference - Points
#     0.0    -   10
#     0.5    -   9
#     1.0    -   8
#     1.5    -   7
#     2.0    -   6
#     2.5    -   5
#     3.0    -   4
#     3.5    -   3
#     4.0    -   2
#     4.5    -   1
#
# SYSTEM = 2
# /u/d_anda from reddit's recommended point spread:
# Difference - Points
#     0.0    -   10
#     0.5    -   8
#     1.0    -   6
#     1.5    -   5
#     2.0    -   4
#     2.5    -   3
#     3.0    -   2
#     3.5    -   1
#     4.0    -   0.5
#     4.5    -   0
#
# SYSTEM = 3
# This system takes the actual ratings into account.
# Same ratings = 10 points
#   (Bonus: 15 pts if same 5 rating, 12 points if same 4.5 or 0.5 rating, and 10.5 points if same 4 or 1 rating)
# Rating of 5 = the best, so most important
# So 5.0 to each lower rating = -3.0 points
# 	5.0-4.5 = 7.0 pts
# 	5.0-4.0 = 4.0 pts
# 	5.0-3.5 = 1.0 pts
# 	5.0-3.0 = -2.0 pts
# 	5.0-2.5 = -5.0 pts
# 	5.0-2.0 = -8.0 pts
# 	5.0-1.5 = -11.0 pts
# 	5.0-1.0 = -14.0 pts
# 	5.0-0.5 = -17.0 pts
# For 4.5 to each lower rating, -2.5 pts
# 	4.5-4.0 = 7.5 pts
# 	4.5-3.5 = 5.0 pts
# 	4.5-3.0 = 2.5 pts
# 	4.5-2.5 = 0.0 pts
# 	4.5-2.0 = -2.5 pts
# 	4.5-1.5 = -5.0 pts
# 	4.5-1.0 = -7.5 pts
# 	4.5-0.5 = -10.0 pts
# For 4.0 to each lower rating, -2.0 pts
# 	4.0-3.5 = 8.0 pts
# 	4.0-3.0 = 6.0 pts
# 	4.0-2.5 = 4.0 pts
# 	4.0-2.0 = 2.0 pts
# 	4.0-1.5 = 0.0 pts
# 	4.0-1.0 = -2.0 pts
# 	4.0-0.5 = -4.0 pts
# For 3.5 to each lower rating, -1.5 pts
# 	3.5-3.0 = 8.5 pts
# 	3.5-2.5 = 7.0 pts
# 	3.5-2.0 = 5.5 pts
# 	3.5-1.5 = 4.0 pts
# 	3.5-1.0 = 2.5 pts
# 	3.5-0.5 = 1.0 pts
# For 3.0 to each lower rating, -1.0 pts
# 	3.0-2.5 = 9.0 pts
# 	3.0-2.0 = 8.0 pts
# 	3.0-1.5 = 7.0 pts
# 	3.0-1.0 = 6.0 pts
# 	3.0-0.5 = 5.0 pts
# For 2.5 to each lower rating, -0.75 pts
# 	2.5-2.0 = 9.25 pts
# 	2.5-1.5 = 8.50 pts
# 	2.5-1.0 = 7.75 pts
# 	2.5-0.5 = 7.00 pts
# For 2.0 to each lower rating, -0.5 pts
# 	2.0-1.5 = 9.5 pts
# 	2.0-1.0 = 9.0 pts
# 	2.0-0.5 = 8.5 pts
# For 1.5 to each lower rating, -0.5 pts
# 	1.5-1.0 = 9.5 pts
# 	1.5-0.5 = 9.0 pts
# For 1.0 to each lower rating, -0.5 pts
# 	1.0-0.5 = 9.5 pts
########################

## Note: figure out what this is doing and add comments.
############################################################
# Function that gives every location of substring in string:
# INPUTS:
#   substring = string (any)
#   string    = string (any)
##################################
def findstrings(substring,string):
	lastfound = -1
	while True:
		lastfound = string.find(substring,lastfound+1)
		if lastfound == -1:  
			break
		yield lastfound

####################################################################################
# Function that grabs all desired substrings that are surrounded by 2 given strings:
# INPUTS:
#   which      = string ('first', 'last', 'all')
#   prestring  = string (any)
#   poststring = string (any)
#   source     = string (the source from which to grab the desired strings)
# OUTPUTS:
#   strings = string or string array (whatever was wanted)
##################################################
def getstrings(which,prestring,poststring,source):
	# First find the start of the number of pages string:
	length = len(prestring)
	prevalue = list(findstrings(prestring,source))
	# If first instance wanted:
	if which == 'first':
		prevalue = [prevalue[0]+length]
	# If last instance wanted:
	elif which == 'last':
		prevalue = [prevalue[-1]+length]
	# If all instances wanted:
	elif which == 'all':
		prevalue = [item+length for item in prevalue]
	else:
		sys.exit('ERROR - in function "getstrings" - Invalid input for "which"')
	# Find the location of the end of string, and get the strings:
	strings = []
	for beginning in prevalue:
		end = source.find(poststring,beginning)
		value = source[beginning:end]
		strings = strings+[value]
	# If just one string desired, return a scalar, otherwise return the array:
	if which == 'first' or which == 'last':
		return strings[0]
	elif which == 'all':
		return strings

##############################################
# Functions that computes the similarity score:
# INPUTS:
#   rating1 = float (can be 0, 0.5, 1, 1.5, 2 2.5, 3, 3.5, 4, 4.5, 5)
#   rating2 = float (can be 0, 0.5, 1, 1.5, 2 2.5, 3, 3.5, 4, 4.5, 5)
#   system  = integer (can be 1, 2, 3)
# OUTPUTS:
#   result = float (between 1 and 10 for system 1, between 0 and 10 for system 2, between -17 and 15 for system 3)
#######################################
def similarity(rating1,rating2,system):
	# Get the absolute difference in ratings for systems 1 & 2:
	diff = abs(rating1-rating2)
	# SYSTEM 1 (see above for details)
	if system == 1:
		diffs =  [0.0,  0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
		points = [10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
		if   diff == diffs[0]:
			result = points[0]
		elif diff == diffs[1]:
			result = points[1]
		elif diff == diffs[2]:
			result = points[2]
		elif diff == diffs[3]:
			result = points[3]
		elif diff == diffs[4]:
			result = points[4]
		elif diff == diffs[5]:
			result = points[5]
		elif diff == diffs[6]:
			result = points[6]
		elif diff == diffs[7]:
			result = points[7]
		elif diff == diffs[8]:
			result = points[8]
		elif diff == diffs[9]:
			result = points[9]
		else:
			sys.exit('ERROR - in function "similarity" - Ratings difference in system 1 is not valid')
	# SYSTEM 2 (see above for details)
	elif system == 2:
		diffs =  [0.0,  0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
		points = [10.0, 8.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.5, 0.0]
		if   diff == diffs[0]:
			result = points[0]
		elif diff == diffs[1]:
			result = points[1]
		elif diff == diffs[2]:
			result = points[2]
		elif diff == diffs[3]:
			result = points[3]
		elif diff == diffs[4]:
			result = points[4]
		elif diff == diffs[5]:
			result = points[5]
		elif diff == diffs[6]:
			result = points[6]
		elif diff == diffs[7]:
			result = points[7]
		elif diff == diffs[8]:
			result = points[8]
		elif diff == diffs[9]:
			result = points[9]
		else:
			sys.exit('ERROR - in function "similarity" - Ratings difference in system 2 is not valid')
	# SYSTEM 3 (see above for details)
	elif system == 3:
		# Same ratings get 10 points, and more meaningful matches get extra points:
		#   (15 points for match 5, 12 points for matchin 4.5 or 0.5, and 10.5 points for matching 4 or 1)
		if rating1 == rating2:
			if rating1 == 5.0:
				result = 15.0
			elif rating1 == 4.5 or rating1 == 0.5:
				result = 12.0
			elif rating1 == 4.0 or rating1 == 1.0:
				result = 10.5
			else:
				result = 10.0
		# Otherwise follow the rating-dependent system for the difference:
		else:
			# Find the highest and lowest rating:
			maxrating = max([rating1,rating2])
			minrating = min([rating1,rating2])
			# Then the size of the gaps between point values depend on that highest rating:
			if maxrating == 5.0:
				gap = 3.0
			elif maxrating == 4.5:
				gap = 2.5
			elif maxrating == 4.0:
				gap = 2.0
			elif maxrating == 3.5:
				gap = 1.5
			elif maxrating == 3.0:
				gap = 1.0
			elif maxrating == 2.5:
				gap = 0.75
			elif maxrating == 2.0 or maxrating == 1.5 or maxrating == 1.0:
				gap = 0.5
			else:
				sys.exit('ERROR - in function "similarity" - Ratings in system 3 are not valid')
			# Then use the formula with the given points gap to find the points for this difference:
			result = 10.0-gap*(maxrating-minrating)/0.5
	else:
		sys.exit('ERROR - in function "similarity" - System option chosen isn\'t available')
	# Return the similarity score:
	return result

##############################################
# Function to grab a user's films and ratings:
# INPUTS:
#   verbose    = integer (0 or 1)
#   user       = string (a valid Letterboxd user)
#   useratings = string ('use' or 'new')
# OUTPUTS:
#   films   = string array (list of user's films)
#   ratings = integer array (integers from 1 to 10, a list of their rating for each film)
#######################################
def userfilms(verbose,user,useratings):
	# First, if using available ratings, check if they exist:
	ratingsflag = 1
	if useratings == 'use':
		priorratingspath = Path('UserFilms/'+user+'_ratings.csv')
		if priorratingspath.exists():
			if verbose == 1:
				print('Using existing ratings file for '+user+'!\n')
			ratingsflag = 0
			# If they exist, read them in:
			films = []
			ratings = []
			with open('UserFilms/'+user+'_ratings.csv') as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=',')
				for row in csv_reader:
					films = films+[row[0]]
					ratings = ratings+[row[1]]
	# If ratings file doesn't exist or new ratings wanted:
	if ratingsflag == 1:
		# The base url of the user's film ratings:
		url = 'https://letterboxd.com/'+user+'/films/ratings/'
		# Grab source code for first ratings page:
		r = requests.get(url)
		source = r.text
		# Check if there aren't any ratings:
		if source.find('No ratings yet') != -1:
			films = ['-1']
			ratings = [-1]
		# If there are ratings, get them:
		else:
			# Find the number of ratings pages:
			# First check if there's only one page:
			pageflag = 0
			if source.find('/'+user+'/films/ratings/page/') == -1:
				pageflag = 1
			# If not, find the number of pages given in the webpage source code:
			else:
				pages = int(getstrings('last','/'+user+'/films/ratings/page/','/"',source))
			# Loop through all pages and grab all the film titles:
			# Initialize results:
			films = []
			ratings = []
			# Start on page 1, get the films:
			films = films+getstrings('all','data-film-slug="/film/','/"',source)
			# Do the same for ratings:
			ratings = ratings+getstrings('all','rating rated-','">',source)
			# Now loop through the rest of the pages:
			if pageflag == 0:
				for page in range(pages-1):
					# Start on page 2:
					page = str(page + 2)
					# Grab source code of the page:
					r = requests.get(url+'page/'+page+'/')
					source = r.text
					# Get films:
					films = films+getstrings('all','data-film-slug="/film/','/"',source)
					# Get ratings:
					ratings = ratings+getstrings('all','rating rated-','">',source)
			# Make sure the lengths match:
			if len(films) != len(ratings):
				sys.exit('ERROR - in function "userfilms" - Number of films does not match number of ratings')
		# Write out ratings to file:
		with open('UserFilms/'+user+'_ratings.csv', mode='w') as outfile:
			csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for i in range(len(films)):
				csvwriter.writerow([films[i],ratings[i]])
	# Ratings should be integer type:
	ratings = [int(item) for item in ratings]
	# Return the results:
	return films,ratings

###############################################################
# Function to grab who a user if following, or their followers:
# INPUTS:
#   user = string (valid Letterboxd user)
#   what = string ('following', 'followers', 'both')
# OUTPUTS:
#   users = string array (list of following/followers names)
##########################
def userfollow(user,what):
	# following, followers, or both?
	if what == 'following':
		what = ['following']
	elif what == 'followers':
		what = ['followers']
	elif what == 'both':
		what = ['following','followers']
	# Initialize results:
	users = []
	for i in range(len(what)):
		# The base url of following or followers:
		url = 'https://letterboxd.com/'+user+'/'+what[i]+'/'
		# Grab source code for first page:
		r = requests.get(url)
		source = r.text
		# Start on page 1:
		# Find the users:
		users = users+getstrings('all','class="avatar -a40" href="/','/"',source)
		# Now loop through the rest of the pages:
		page = 2
		# Check if a second page exists:
		lastpage = '<div class="paginate-nextprev paginate-disabled"><span class="next">'
		if source.find(lastpage) == -1:
			flag = 0
		else:
			flag = 1
		while flag == 0:
			# Grab source code of the page:
			r = requests.get(url+'page/'+str(page)+'/')
			source = r.text
			# Check if it's the last page:
			if source.find(lastpage) != -1:
				flag = 1
			# Find the users:
			users = users+getstrings('all','class="avatar -a40" href="/','/"',source)
			# Advance the page
			page = page+1
	# Take only unique users:
	users = list(set(users))
	# Return results
	return users

#########################################################
# Function to match two lists of films and their ratings:
# INPUTS:
#   films1   = string array (list of user1 films)
#   ratings1 = integer array (list of corresponding user1 ratings)
#   films2   = string array (list of user2 films)
#   ratings2 = integer array (list of corresponding user2 ratings)
# OUTPUTS:
#   finalfilms    = string array (list of matched films)
#   finalratings1 = integer array (list of corresponding user1 ratings)
#   finalratings2 = integer array (list of corresponding user2 ratings)
###############################################
def filmmatch(films1,ratings1,films2,ratings2):
	# Create master lists:
	finalfilms = []
	finalratings1 = []
	finalratings2 = []
	# Start from the shorter list,
	# Find if any films match,
	# Removing finished elements.
	# If films1 list happens to be shorter:
	if len(films1) < len(films2):
		while len(films1) > 0:
			i = 0
			flag = 0
			# Until a match is found or all films are checked, loop through films:
			while flag == 0:
				# If a match is found, record it:
				if films2[i] == films1[0]:
					flag = 1
					finalfilms = finalfilms+[films1[0]]
					finalratings1 = finalratings1+[ratings1[0]]
					finalratings2 = finalratings2+[ratings2[i]]
					# Film is found, delete it from films2 list:
					del films2[i]
					del ratings2[i]
				# If a match isn't found, check next film:
				else:
					i = i+1
					# If all films checked, no match found:
					if i == len(films2):
						flag = 1
			# Film either matched or not, delete it from films1 list
			del films1[0]
			del ratings1[0]
	# If films2 list happens to be shorter:
	else:
		while len(films2) > 0:
			i = 0
			flag = 0
			# Until a match is found or all films are checked, loop through films:
			while flag == 0:
				# If a match is found, record it:
				if films1[i] == films2[0]:
					flag = 1
					finalfilms = finalfilms+[films2[0]]
					finalratings1 = finalratings1+[ratings1[i]]
					finalratings2 = finalratings2+[ratings2[0]]
					# Film is found, delete it from films1 list:
					del films1[i]
					del ratings1[i]
				# If a match isn't found, check next film:
				else:
					i = i+1
					if i == len(films1):
						flag = 1
			# Film either matched or not, delete it from films2 list
			del films2[0]
			del ratings2[0]
	# If no matches at all found:
	if len(finalfilms) == 0 and len(finalratings1) == 0 and len(finalratings2) == 0:
		finalfilms = ['-1']
		finalratings1 = [-1]
		finalratings2 = [-1]
	# Return the results
	return finalfilms,finalratings1,finalratings2

##############################################
# Function to compute final similarity scores:
# INPUTS:
#   finalfilms    = string array (matched films)
#   finalratings1 = float array (matched films user1 ratings)
#   finalratings2 = float array (matched films user2 ratings)
#   system        = integer (1, 2, 3)
# OUTPUTS:
#   result = float (average points between all matched films)
###########################################################
def scoring(finalfilms,finalratings1,finalratings2,system):
	# Loop through every matched film rating and compute similarity score:
	finalpoints = []
	for i in range(len(finalfilms)):
		rating1 = finalratings1[i]/2.0
		rating2 = finalratings2[i]/2.0
		points = similarity(rating1,rating2,system)
		finalpoints = finalpoints+[points]
	# Take the average of all values:
	result = np.mean(finalpoints)
	# If the result is >10 or <0 for whatever reason, limit them to the extremes:
	if result > 10.0:
		result = 10.0
	elif result < 0.0:
		result = 0.0
	return result

######################################
# Function to interpret ratings match:
# INPUTS:
#   spreadyes   = integer (0 or 1)
#   rating      = float (the similarity score to interpret)
#   spreadmidpt = 
# OUTPUTS:
#################################################################
def ratinginterpretation(spreadyes,rating,spreadmidpt,spreadval):
	# If there isn't a prior spread, use default:
	# 0-2:  Worst match
	# 2-3:  Terrible match
	# 3-4:  Really bad match
	# 4-5:  Bad match
	# 5-6:  Poor match
	# 6-7:  Typical match
	# 7-8:  Good match
	# 8-9:  Great match
	# 9-10: Amazing match
	if spreadyes == 0:
		if rating > 10.0:
			sys.exit('ERROR - in function "ratinginterpretation" - Similarity score is >10')
		elif rating > 9.0:
			return 'Amazing match'
		elif rating > 8.0:
			return 'Great match'
		elif rating > 7.0:
			return 'Good match'
		elif rating > 6.0:
			return 'Typical match'
		elif rating > 5.0:
			return 'Poor match'
		elif rating > 4.0:
			return 'Bad match'
		elif rating > 3.0:
			return 'Really bad match'
		elif rating > 2.0:
			return 'Terrible match'
		elif rating >= 0.0:
			return 'Worst match'
		else:
			sys.exit('ERROR - in function "ratinginterpretation" - Similarity score is <0')
	# Otherwise extract from the data:
	elif spreadyes == 1:
		ratings = []
		# Combine the saved spread and compute the mean and standard deviation:
		for i in range(len(spreadval)):
			ratings = ratings+[spreadmidpt[i] for val in range(spreadval[i])]
		spreadmean = np.mean(ratings)
		spreadstddev = np.std(ratings)
		# Interpret the similarity score based on mean and standard deviations:
		if rating > 10.0:
			sys.exit('ERROR - in function "ratinginterpretation" - Similarity score is >10')
		if rating > spreadmean+2.0*spreadstddev:
			return 'Amazing match'
		elif rating > spreadmean+1.5*spreadstddev:
			return 'Great match'
		elif rating > spreadmean+1.0*spreadstddev:
			return 'Good match'
		elif rating > spreadmean+0.0*spreadstddev:
			return 'Typical match'
		elif rating > spreadmean-1.0*spreadstddev:
			return 'Poor match'
		elif rating > spreadmean-1.5*spreadstddev:
			return 'Bad match'
		elif rating > spreadmean-2.0*spreadstddev:
			return 'Really bad match'
		elif rating > spreadmean-2.5*spreadstddev:
			return 'Terrible match'
		elif rating >= 0.0:
			return 'Worst match'
		else:
			sys.exit('ERROR - in function "ratinginterpretation" - Similarity score is <0')

###############################################
# Function to read in and parse the input file:
#
#
#################################
def inputread(verbose,inputfile):
	# Read in the whole input file:
	with open(inputfile) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=' ',skipinitialspace=True)
		keyword = []
		equals = []
		parameter = []
		for row in csv_reader:
			if len(row) == 3:
				keyword = keyword+[row[0]]
				equals = equals+[row[1]]
				parameter = parameter+[row[2]]
	# Get parameters:
	for i in range(len(keyword)):
		# user1
		if keyword[i] == 'user1' and equals[i] == '=':
			user1 = parameter[i]
		# user2
		if keyword[i] == 'user2' and equals[i] == '=':
			user2 = parameter[i]
		# system
		if keyword[i] == 'system' and equals[i] == '=':
			system = int(parameter[i])
		# useratings
		if keyword[i] == 'useratings' and equals[i] == '=':
			useratings = parameter[i]
		# tocompute
		if keyword[i] == 'tocompute' and equals[i] == '=':
			tocompute = parameter[i]
		# spreadchoice
		if keyword[i] == 'spreadchoice' and equals[i] == '=':
			spreadchoice = parameter[i]
		# outtxtchoice
		if keyword[i] == 'outtxtchoice' and equals[i] == '=':
			outtxtchoice = parameter[i]
		# outcsvchoice
		if keyword[i] == 'outcsvchoice' and equals[i] == '=':
			outcsvchoice = parameter[i]
	return user1,user2,system,useratings,tocompute,spreadchoice,outtxtchoice,outcsvchoice

############################
#### START MAIN PROGRAM ####
############################

# Grabs values entered through execution, i.e. python user_film_compare.py input.txt 1
# For an input file called 'input.txt' and verbose = 1 (print out info)
inputs = sys.argv
inputfile = inputs[1]
verbose = int(inputs[2])

# Make sure inputs are valid:
inpath = Path(inputfile)
if not(inpath.exists()):
	sys.exit('ERROR - in main program - Input file does not exist')
if verbose != 0 and verbose != 1:
	sys.exit('ERROR - in main program - Verbose not 0 or 1')

# Read in input file:
user1,user2,system,useratings,tocompute,spreadchoice,outtxtchoice,outcsvchoice = inputread(verbose,inputfile)

# Beginning text and timing:
if verbose == 1:
	print('\n**Note**')
	print('For a fresh run, each user takes about 30 seconds to process.')
	print('So, comparing two users takes about 1 minute.')
	print('When comparing to following or followers, here are some estimations:')
	print('      10 users = 5 minutes')
	print('     100 users = 1 hour')
	print('    1000 users = 8 hours')
	print('These times will be greatly shortened if user film files already exist.')
	print('\nSystems:')
	print('1 = even difference points between 1 and 10')
	print('2 = manual distribution in point differences by reddit user /u/d_anda')
	print('3 = complex point system by aes, giving different points depending on actual ratings (RECOMMENDED)')
starttime = datetime.now().timestamp()
times = []

# The two users being compared, or if all friends are being compared:
#user1 = input(f"\nLetterboxd Username 1:\n")
#user2 = input(f"\nLetterboxd Username 2, or 'following' or 'followers' or 'both':\n")
#system = input(f"\nSystem:\n")
#useratings = input(f"\nUse saved rating if available, or get all new ratings? (use/new)\n")

# Check for prior spread file:
spreadyes = 0
spreadpath1 = Path('Spreads/'+user1+'_both_'+str(system)+'_spread.txt')
spreadpath2 = Path('Spreads/'+user1+'_following_'+str(system)+'_spread.txt')
spreadpath3 = Path('Spreads/'+user1+'_followers_'+str(system)+'_spread.txt')
spreadmidpt = []
spreadval = []
if spreadpath1.exists():
	spreadyes = 1
	with open('Spreads/'+user1+'_both_'+str(system)+'_spread.txt') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=' ')
		for row in csv_reader:
			spreadmidpt = spreadmidpt+[float(row[0])]
			spreadval = spreadval+[int(row[1])]
elif spreadpath2.exists():
	spreadyes = 1
	with open('Spreads/'+user1+'_following_'+str(system)+'_spread.txt') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=' ')
		for row in csv_reader:
			spreadmidpt = spreadmidpt+[float(row[0])]
			spreadval = spreadval+[int(row[1])]
elif spreadpath3.exists():
	spreadyes = 1
	with open('Spreads/'+user1+'_followers_'+str(system)+'_spread.txt') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=' ')
		for row in csv_reader:
			spreadmidpt = spreadmidpt+[float(row[0])]
			spreadval = spreadval+[int(row[1])]

# If just two users are being compared:
if user2 != 'following' and user2 != 'followers' and user2 != 'both':
	if verbose == 1:
		print('\nThe users being compared are '+user1+' and '+user2+'\n')
	flag = 0

	# Working on user1:
	if verbose == 1:
		print('Grabbing all film ratings from '+user1+'\n')
	films1,ratings1 = userfilms(verbose,user1,useratings)
	if films1[0] == '-1' and ratings1[0] == -1:
		if verbose == 1:
			print(user1+' has no ratings!\n')
		flag = 1
	
	# Working on user2:
	if verbose == 1:
		print('Grabbing all film ratings from '+user2+'\n')
	films2,ratings2 = userfilms(verbose,user2,useratings)
	if films2 == '-1' and ratings2 == -1:
		if verbose == 1:
			print(user2+' has no ratings!\n')
		flag = 1
	
	# Find all matching films:
	if flag == 0:
		if verbose == 1:
			print('Finding matching films\n')
		oglength1 = len(films1)
		oglength2 = len(films2)
		finalfilms,finalratings1,finalratings2 = filmmatch(films1,ratings1,films2,ratings2)
		if finalfilms[0] == '-1' and finalratings1[0] == -1 and finalratings2[0] == -1:
			finalfilms = []
		# Find longest username for a neat output:
		longest = len(max([user1+' ratings:',user2+' ratings:','matched films:'],key=len))
		if verbose == 1:
			print('{:{longest}} {:d}'.format(user1+' ratings:',oglength1,longest=longest))
			print('{:{longest}} {:d}'.format(user2+' ratings:',oglength2,longest=longest))
			print('{:{longest}} {:d}{}'.format('matched films:',len(finalfilms),'\n',longest=longest))

		# Get the similarity score and print results:
		if len(finalfilms) > 0:
			results = scoring(finalfilms,finalratings1,finalratings2,system)
			if verbose == 1:
				print('RESULTS = {:.3f}{}'.format(results,'\n'))
				print('MATCH RATING = '+ratinginterpretation(spreadyes,results,spreadmidpt,spreadval)+'\n')
		else:
			if verbose == 1:
				print('No film matches found.\n')
	else:
		if verbose == 1:
			print('No films to match.\n')

	# Print final timing:
	totaltime = datetime.now().timestamp()-starttime
	if verbose == 1:
		print('Total time (s) = {:.3f}{}'.format(totaltime,'\n'))

# Else go through following or followers
else:

	# Find all following or followers:
	if verbose == 1:
		if user2 == 'following':
			print('\nGrabbing all users that '+user1+' is following\n')
		elif user2 == 'followers':
			print('\nGrabbing all users that follow '+user1+'\n')
		elif user2 == 'both':
			print('\nGrabbing all users that both follow '+user1+' and who '+user1+' is following\n')
	users = userfollow(user1,user2)
	if verbose == 1:
		print('There are '+str(len(users)))

	# Check if all or some should be computed:
	#tocompute = input(f"\nChoose a number to compute:\n")
	if tocompute == 'all':
		tocompute = len(users)
	elif int(tocompute) > len(users):
		tocompute = len(users)
	else:
		tocompute = int(tocompute)
	if int(tocompute) >= 0 and int(tocompute) <= len(users):
		users = users[:int(tocompute)]
	else:
		sys.exit("ERROR - in 'else' of main program - Invalid number entered.")

	# Compute similarity score for all or some users:
	# Just need to grab films for user1 once:
	if verbose == 1:
		print('\nGrabbing all film ratings from '+user1+'\n')
	films1,ratings1 = userfilms(verbose,user1,useratings)
	if films1[0] == '-1' and ratings1[0] == -1:
		sys.exit("ERROR - in 'else' of main program - User 1 does not have any ratings.")
	oglength1 = len(films1)
	# Initialize results:
	scores = []
	interpretations = []
	loopstarttime = datetime.now().timestamp()
	for i in range(len(users)):
		if verbose == 1:
			print('Comparing with '+users[i]+' ('+str(i+1)+'/'+str(len(users))+')')
		flag = 0
		films2,ratings2 = userfilms(verbose,users[i],useratings)
		if films2[0] == '-1' and ratings2[0] == -1:
			if verbose == 1:
				print(users[i]+' has no ratings.\n')
			flag = 1
		if flag == 0:
			oglength2 = len(films2)
			newfilms1 = [value for value in films1]
			newratings1 = [value for value in ratings1]
			finalfilms,finalratings1,finalratings2 = filmmatch(newfilms1,newratings1,films2,ratings2)
			if finalfilms[0] == '-1' and finalratings1[0] == -1 and finalratings2[0] == -1:
				finalfilms = []
			if len(finalfilms) > 0:
				results = scoring(finalfilms,finalratings1,finalratings2,system)
				interpretation = ratinginterpretation(spreadyes,results,spreadmidpt,spreadval)
				scores = scores+[results]
				interpretations = interpretations+[interpretation]
			else:
				scores = scores+[-1]
				interpretations = interpretations+['N/A']
			# Find longest username for a neat output:
			longest = len(max([user1+' ratings:',users[i]+' ratings:','matched films:'],key=len))
			if verbose == 1:
				print('{:{longest}} {:d}'.format(user1+' ratings:',oglength1,longest=longest))
				print('{:{longest}} {:d}'.format(users[i]+' ratings:',oglength2,longest=longest))
				print('{:{longest}} {:d}'.format('matched films:',len(finalfilms),longest=longest))
			if len(finalfilms) > 0:
				if verbose == 1:
					print('compatibility: {:.5f}'.format(results))
					print('match rating = '+interpretation)
			else:
				if verbose == 1:
					print('No film matches found.')
			elapsedtime = datetime.now().timestamp()-starttime
			if verbose == 1:
				print('time elapsed (m) = {:.3f}'.format(elapsedtime/60.0))
			loopelapsedtime = datetime.now().timestamp()-loopstarttime
			timeperloop = loopelapsedtime/(i+1.0)
			estimatedtime = (len(users)-(i+1.0))*timeperloop
			times = times+[estimatedtime+elapsedtime]
			# Add 1 standard deviation to the average time to give a buffer:
			avgtime = np.mean(times)+np.std(times)
			# If the loop is done, no time remaining:
			if i == len(users)-1:
				if verbose == 1:
					print('estimated time remaining (m) = {:.3f}{}'.format(0.0,'\n'))
			# Otherwise estimate time remaining:
			else:
				if verbose == 1:
					print('estimated time remaining (m) = {:.3f}{}'.format((avgtime-elapsedtime)/60.0,'\n'))
		else:
			scores = scores+[-1]
			interpretations = interpretations+['N/A']

	# Sort all the scores:
	sortedusers = [name for number,name in sorted(zip(scores,users))]
	sortedusers.reverse()
	sortedinterpretations = [name for number,name in sorted(zip(scores,interpretations))]
	sortedinterpretations.reverse()
	scores.sort()
	scores.reverse()

	# Print out results:
	if verbose == 1:
		if user2 == 'both':
			print('Comparing '+user1+' following and followers\n')
		else:
			print('Comparing '+user1+' '+user2+'\n')
	# Find longest username for a neat output:
	longest = len(max(sortedusers,key=len))
	for i in range(len(sortedusers)):
		if verbose == 1:
			print('{:{longest}} -- {:8.5f} -- {}'.format(sortedusers[i],scores[i],sortedinterpretations[i],longest=longest))

	# Print final timing:
	totaltime = datetime.now().timestamp()-starttime
	if verbose == 1:
		print('{}Total time (m) = {:.3f}{}'.format('\n',totaltime/60.0,'\n'))

	# Check if previous file exists for the current configuration:
	newspread = 1
	spreadpath = Path('Spreads/'+user1+'_'+user2+'_'+str(system)+'_spread.txt')
	if spreadpath.exists():
		if verbose == 1:
			print('Previous spread found')
		# Ask if new file should be written:
		#spreadchoice = input(f"\nCompute new spread and overwrite the previous? (y/n):\n")
		if verbose == 1:
			print('')
		if spreadchoice != "y":
			newspread = 0
	if newspread == 1:
		# remove any "-1" values from the scores:
		cutscores = []
		cutusers = []
		cutinterpretations = []
		for i in range(len(scores)):
			if scores[i] >= 0.0:
				cutscores = cutscores+[scores[i]]
				cutusers = cutusers+[sortedusers[i]]
				cutinterpretations = cutinterpretations+[sortedinterpretations[i]]
		spreadfile = open('Spreads/'+user1+'_'+user2+'_'+str(system)+'_spread.txt','w')
		bins = [0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10]
		width = bins[1]-bins[0]
		hist,bin_edges = np.histogram(cutscores,bins=bins)
		midpoints = [bins[i]-(width/2.0) for i in range(len(bins))[1:]]
		for i in range(len(hist)):
			spreadfile.write(str(midpoints[i])+' '+str(hist[i])+'\n')
		plt.plot(midpoints,hist)
		plt.xlabel('Compatibility Rating')
		plt.ylabel('Number In Bin')
		plt.savefig('Spreads/'+user1+'_'+user2+'_'+str(system)+'_spread_plot.png')
		spreadfile.close()

	# Create output files, if necessary/wanted:
	newouttxt = 1
	newoutcsv = 1
	outpathtxt = Path('Output/'+user1+'_'+user2+'_'+str(system)+'_output.txt')
	outpathcsv = Path('Output/'+user1+'_'+user2+'_'+str(system)+'_output.csv')
	if outpathtxt.exists():
		if verbose == 1:
			print('Previous text output found')
		# Ask if new text file should be written:
		#outtxtchoice = input(f"\nOverwrite the previous text output? (y/n):\n")
		if verbose == 1:
			print('')
		if outtxtchoice != "y":
			newouttxt = 0
	if outpathcsv.exists():
		if verbose == 1:
			print('Previous CSV output found')
		# Ask if new CSV file should be written:
		#outcsvchoice = input(f"\nOverwrite the previous CSV output? (y/n):\n")
		if verbose == 1:
			print('')
		if outcsvchoice != "y":
			newoutcsv = 0
	if newouttxt == 1:
		outfile = open('Output/'+user1+'_'+user2+'_'+str(system)+'_output.txt','w')
		for i in range(len(sortedusers)):
			outfile.write('{:{longest}} {:8.5f}  {}{}'.format(sortedusers[i],scores[i],sortedinterpretations[i],'\n',longest=longest))
		# Close output file:
		outfile.close()
	if newoutcsv == 1:
		with open('Output/'+user1+'_'+user2+'_'+str(system)+'_output.csv', mode='w') as outfile:
			csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for i in range(len(sortedusers)):
				csvwriter.writerow([sortedusers[i],scores[i],sortedinterpretations[i]])
