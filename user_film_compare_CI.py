import requests
import sys
from datetime import datetime
#import os.path
#from os import path
import numpy as np
import matplotlib.pyplot as plt
import statistics

##
## Written by Alex Spacek
## March 2020 - March 2020
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

############################################################
# Function that gives every location of substring in string:
def findstrings(substring,string):
	lastfound = -1
	while True:
		lastfound = string.find(substring,lastfound+1)
		if lastfound == -1:  
			break
		yield lastfound

##############################################
# Functions that computes the similarity score:
def similarity(rating1,rating2,system):
	diff = abs(rating1-rating2)
	if system == '1':
		switcher={
			0.0:10,
			0.5:9,
			1.0:8,
			1.5:7,
			2.0:6,
			2.5:5,
			3.0:4,
			3.5:3,
			4.0:2,
			4.5:1,
		}
		return switcher.get(diff,"Error in rating difference")
	elif system == '2':
		switcher={
			0.0:10,
			0.5:8,
			1.0:6,
			1.5:5,
			2.0:4,
			2.5:3,
			3.0:2,
			3.5:1,
			4.0:0.5,
			4.5:0,
		}
		return switcher.get(diff,"Error in rating difference")
	elif system == '3':
		if rating1 == rating2:
			if rating1 == 5.0:
				result = 15.0
			elif rating1 == 4.5 or rating1 == 0.5:
				result = 12.0
			elif rating1 == 4.0 or rating1 == 1.0:
				result = 10.5
			else:
				result = 10.0
		else:
			maxrating = max([rating1,rating2])
			minrating = min([rating1,rating2])
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
			result = 10.0-gap*(maxrating-minrating)/0.5
		return result
	else:
		sys.exit("System option chosen isn't available")

##############################################
# Function to grab a user's films and ratings:
def userfilms(user):

	# The base url of the user's film ratings:
	url = 'https://letterboxd.com/'+user+'/films/ratings/'
	# Grab source code for first ratings page:
	r = requests.get(url)
	source = r.text
	
	# Check if there are any ratings:
	if source.find('No ratings yet') != -1:
		films = -1
		ratings = -1
	else:

		# Find the number of ratings pages:
		# First check if there's only one page:
		pageflag = 0
		if source.find('/'+user+'/films/ratings/page/') == -1:
			pageflag = 1
		else:
			# First find the start of the number of pages:
			length = len('/'+user+'/films/ratings/page/')
			prepages = list(findstrings('/'+user+'/films/ratings/page/',source))
			prepages = prepages[-1]+length
			# Then find the end:
			postpages = source.find('/"',prepages+1)
			# The number is found between:
			pages = int(source[prepages:postpages])
		
		# Loop through all pages and grab all the film titles:
		# Initialize results:
		films = []
		ratings = []
		
		# Start on page 1:
		# Find the location of the start of each film title:
		length = len('data-film-slug="/film/')
		prefilms = list(findstrings('data-film-slug="/film/',source))
		prefilms = [value+length for value in prefilms]
		# Find the location of the end of each film title, and get the titles:
		for value in prefilms:
			end = source.find('/"',value)
			film = source[value:end]
			films = films+[film]
		# Do the same for ratings:
		# Find the location of the start of each rating:
		length = len('rating rated-')
		preratings = list(findstrings('rating rated-',source))
		preratings = [value+length for value in preratings]
		# Find the location of the end of each rating, and get the ratings:
		for value in preratings:
			end = source.find('">',value)
			rating = source[value:end]
			ratings = ratings+[rating]
		
		# Now loop through the rest of the pages:
		if pageflag == 0:
			for page in range(pages-1):
				# Start on page 2:
				page = str(page + 2)
				# Grab source code of the page:
				r = requests.get(url+'page/'+page+'/')
				source = r.text
				# Find the location of the start of each film title:
				length = len('data-film-slug="/film/')
				prefilms = list(findstrings('data-film-slug="/film/',source))
				prefilms = [value+length for value in prefilms]
				# Find the location of the end of each film title, and get the titles:
				for value in prefilms:
					end = source.find('/"',value)
					film = source[value:end]
					films = films+[film]
				# Do the same for ratings:
				# Find the location of the start of each rating:
				length = len('rating rated-')
				preratings = list(findstrings('rating rated-',source))
				preratings = [value+length for value in preratings]
				# Find the location of the end of each rating, and get the ratings:
				for value in preratings:
					end = source.find('">',value)
					rating = source[value:end]
					ratings = ratings+[rating]
		
		# Make sure the lengths match:
		if len(films) != len(ratings):
			sys.exit("Number of films does not match number of ratings")

	# Return the results:
	return films,ratings

##############################################
# Function to grab who a user if following, or their followers:
def userfollow(user,what):
	# The base url of following or followers:
	url = 'https://letterboxd.com/'+user+'/'+what+'/'
	
	# Grab source code for first page:
	r = requests.get(url)
	source = r.text
	
	# Initialize results:
	users = []
	
	# Start on page 1:
	# Find the location of the start of each user:
	length = len('class="avatar -a40" href="/')
	preusers = list(findstrings('class="avatar -a40" href="/',source))
	preusers = [value+length for value in preusers]
	# Find the location of the end of each user, and get the users:
	for value in preusers:
		end = source.find('/"',value)
		user = source[value:end]
		users = users+[user]
	
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
		# Find the location of the start of each user:
		length = len('class="avatar -a40" href="/')
		preusers = list(findstrings('class="avatar -a40" href="/',source))
		preusers = [value+length for value in preusers]
		# Find the location of the end of each user, and get the users:
		for value in preusers:
			end = source.find('/"',value)
			user = source[value:end]
			users = users+[user]
		page = page+1

	# Return results
	return users

#########################################################
# Function to match two lists of films and their ratings:
def filmmatch(films1,ratings1,films2,ratings2):

	# Create master lists:
	finalfilms = []
	finalratings1 = []
	finalratings2 = []
	# Start from the shorter list,
	# Find if any films match,
	# Removing finished elements:
	if len(films1) < len(films2):
		while len(films1) > 0:
			i = 0
			flag = 0
			while flag == 0:
				if films2[i] == films1[0]:
					flag = 1
					finalfilms = finalfilms+[films1[0]]
					finalratings1 = finalratings1+[ratings1[0]]
					finalratings2 = finalratings2+[ratings2[i]]
					del films2[i]
					del ratings2[i]
				else:
					i = i+1
					if i == len(films2):
						flag = 1
			del films1[0]
			del ratings1[0]
	else:
		while len(films2) > 0:
			i = 0
			flag = 0
			while flag == 0:
				if films1[i] == films2[0]:
					flag = 1
					finalfilms = finalfilms+[films2[0]]
					finalratings1 = finalratings1+[ratings1[i]]
					finalratings2 = finalratings2+[ratings2[0]]
					del films1[i]
					del ratings1[i]
				else:
					i = i+1
					if i == len(films1):
						flag = 1
			del films2[0]
			del ratings2[0]

	# If no matches found:
	if len(finalfilms) == 0 or len(finalratings1) == 0 or len(finalratings2) == 0:
		finalfilms = -1
		finalratings1 = -1
		finalratings2 = -1

	# Return the results
	return finalfilms,finalratings1,finalratings2

##############################################
# Function to compute final similarity scores:
def scoring(finalfilms,finalratings1,finalratings2,system):
	finalpoints = []
	for i in range(len(finalfilms)):
		rating1 = int(finalratings1[i])/2.0
		rating2 = int(finalratings2[i])/2.0
		points = similarity(rating1,rating2,system)
		finalpoints = finalpoints+[points]
	result = sum(finalpoints)/len(finalpoints)
	# If the result is >10 or <0 for whatever reason, limit them to the extremes:
	if result > 10.0:
		result = 10.0
	elif result < 0.0:
		result = 0.0
	return result

############################
#### START MAIN PROGRAM ####
############################

# Beginning text and timing:
print('\n**Note**')
print('Each user takes about 30 seconds to process.')
print('So, comparing two users takes about 1 minute.')
print('When comparing to following or followers, here are some estimations:')
print('      10 users = 5 minutes')
print('     100 users = 1 hour')
print('    1000 users = 8 hours')
print('\nSystems:')
print('1 = even difference points between 1 and 10')
print('2 = manual distribution in point differences by reddit user /u/d_anda')
print('3 = complex point system by aes, giving different points depending on actual ratings (RECOMMENDED)')
starttime = datetime.now().timestamp()
times = []

# The two users being compared, or if all friends are being compared:
user1 = "moogic"
user2 = "blankments"
system = "5"

# If just two users are being compared:
if user2 != 'following' and user2 != 'followers':
	print('\nThe users being compared are '+user1+' and '+user2+'\n')
	flag = 0
	
	# Working on user1:
	print('Grabbing all film ratings from '+user1+'\n')
	films1,ratings1 = userfilms(user1)
	if films1 == -1 or ratings1 == -1:
		print(user1+' has no ratings!\n')
		flag = 1
	
	# Working on user2:
	print('Grabbing all film ratings from '+user2+'\n')
	films2,ratings2 = userfilms(user2)
	if films2 == -1 or ratings2 == -1:
		print(user2+' has no ratings!\n')
		flag = 1
	
	# Find all matching films:
	if flag == 0:
		print('Finding matching films\n')
		oglength1 = len(films1)
		oglength2 = len(films2)
		finalfilms,finalratings1,finalratings2 = filmmatch(films1,ratings1,films2,ratings2)
		if finalfilms == -1 or finalratings1 == -1 or finalratings2 == -1:
			finalfilms = []
		# Find longest username for a neat output:
		longest = len(max([user1+' ratings:',user2+' ratings:','matched films:'],key=len))
		print('{:{longest}} {:d}'.format(user1+' ratings:',oglength1,longest=longest))
		print('{:{longest}} {:d}'.format(user2+' ratings:',oglength2,longest=longest))
		print('{:{longest}} {:d}{}'.format('matched films:',len(finalfilms),'\n',longest=longest))

		# Get the similarity score and print results:
		if len(finalfilms) > 0:
			results = scoring(finalfilms,finalratings1,finalratings2,system)
			print('RESULTS = {:.3f}{}'.format(results,'\n'))
		else:
			print('No film matches found.\n')
	else:
		print('No films to match.\n')

	# Print final timing:
	totaltime = datetime.now().timestamp()-starttime
	print('Total time (s) = {:.3f}{}'.format(totaltime,'\n'))

# Else go through following or followers
else:

	# Find all following or followers:
	if user2 == 'following':
		print('\nGrabbing all users that '+user1+' is following\n')
	else:
		print('\nGrabbing all users that follow '+user1+'\n')
	users = userfollow(user1,user2)
	print('There are '+str(len(users)))

	# Check if all or some should be computed:
	tocompute = "10"
	if int(tocompute) >= 0 and int(tocompute) <= len(users):
		users = users[:int(tocompute)]
	else:
		sys.exit("Invalid number entered.")

	# Compute similarity score for all or some users:
	# Just need to grab films for user1 once:
	print('\nGrabbing all film ratings from '+user1+'\n')
	films1,ratings1 = userfilms(user1)
	if films1 == -1 or ratings1 == -1:
		sys.exit("User 1 does not have any ratings.")
	oglength1 = len(films1)
	# Initialize results:
	scores = []
	loopstarttime = datetime.now().timestamp()
	for i in range(len(users)):
		print('Comparing with '+users[i]+' ('+str(i+1)+'/'+str(len(users))+')')
		flag = 0
		films2,ratings2 = userfilms(users[i])
		if films2 == -1 or ratings2 == -1:
			print(users[i]+' has no ratings.\n')
			flag = 1
		if flag == 0:
			oglength2 = len(films2)
			newfilms1 = [value for value in films1]
			newratings1 = [value for value in ratings1]
			finalfilms,finalratings1,finalratings2 = filmmatch(newfilms1,newratings1,films2,ratings2)
			if finalfilms == -1 or finalratings1 == -1 or finalratings2 == -1:
				finalfilms = []
			if len(finalfilms) > 0:
				results = scoring(finalfilms,finalratings1,finalratings2,system)
				scores = scores+[results]
			else:
				scores = scores+[-1]
			# Find longest username for a neat output:
			longest = len(max([user1+' ratings:',users[i]+' ratings:','matched films:'],key=len))
			print('{:{longest}} {:d}'.format(user1+' ratings:',oglength1,longest=longest))
			print('{:{longest}} {:d}'.format(users[i]+' ratings:',oglength2,longest=longest))
			print('{:{longest}} {:d}'.format('matched films:',len(finalfilms),longest=longest))
			if len(finalfilms) > 0:
				print('compatibility: {:.3f}'.format(results))
			else:
				print('No film matches found.')
			elapsedtime = datetime.now().timestamp()-starttime
			print('time elapsed (m) = {:.3f}'.format(elapsedtime/60.0))
			loopelapsedtime = datetime.now().timestamp()-loopstarttime
			timeperloop = loopelapsedtime/(i+1.0)
			estimatedtime = (len(users)-(i+1.0))*timeperloop
			times = times+[estimatedtime+elapsedtime]
			# Add 1 standard deviation to the average time to give a buffer:
			avgtime = np.mean(times)+np.std(times)
			# If the loop is done, no time remaining:
			if i == len(users)-1:
				print('estimated time remaining (m) = {:.3f}{}'.format(0.0,'\n'))
			# Otherwise estimate time remaining:
			else:
				print('estimated time remaining (m) = {:.3f}{}'.format((avgtime-elapsedtime)/60.0,'\n'))
		else:
			scores = scores+[-1]

	# Sort all the scores:
	sortedusers = [name for number,name in sorted(zip(scores,users))]
	sortedusers.reverse()
	scores.sort()
	scores.reverse()

	# Print out results:
	print('Comparing '+user1+' '+user2+'\n')
	# Find longest username for a neat output:
	longest = len(max(sortedusers,key=len))
	for i in range(len(sortedusers)):
		print('{:{longest}} -- {}'.format(sortedusers[i],scores[i],longest=longest))

	# Print final timing:
	totaltime = datetime.now().timestamp()-starttime
	print('{}Total time (m) = {:.3f}{}'.format('\n',totaltime/60.0,'\n'))

	# Check if previous file exists for the current configuration:
	newspread = 1
	if path.exists('Spreads/'+user1+'_'+user2+'_spread.txt'):
		print('Previous spread found')
		# Ask if new file should be written:
		spreadchoice = "n"
		print('')
		if spreadchoice != "y":
			newspread = 0
	if newspread == 1:
		# remove any "-1" values from the scores:
		cutscores = []
		cutusers = []
		for i in range(len(scores)):
			if scores[i] >= 0.0:
				cutscores = cutscores+[scores[i]]
				cutusers = cutusers+[sortedusers[i]]
		spreadfile = open('Spreads/'+user1+'_'+user2+'_spread.txt','w')
		bins = [0,1,2,3,4,5,6,7,8,9,10]
		hist,bin_edges = np.histogram(cutscores,bins=bins)
		midpoints = [value-0.5 for value in range(len(bins))[1:]]
		for i in range(len(hist)):
			spreadfile.write(str(midpoints[i])+' '+str(hist[i])+'\n')
		plt.plot(midpoints,hist)
		plt.xlabel('Compatibility Rating')
		plt.ylabel('Number In Bin')
		plt.savefig('Spreads/'+user1+'_'+user2+'_spread_plot.png')
		spreadfile.close()

	# Create output file, if necessary/wanted:
	newout = 1
	if path.exists('Output/'+user1+'_'+user2+'_output.txt'):
		print('Previous output found')
		# Ask if new file should be written:
		outchoice = "n"
		print('')
		if spreadchoice != "y":
			newout = 0
	if newout == 1:
		outfile = open('Output/'+user1+'_'+user2+'_output.txt','w')
		for i in range(len(sortedusers)):
			outfile.write('{:{longest}} {}{}'.format(sortedusers[i],scores[i],'\n',longest=longest))
		# Close output file:
		outfile.close()
