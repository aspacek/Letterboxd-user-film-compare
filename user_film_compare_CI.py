import requests
import sys
import datetime

##
## Written by aspacek, March 2020
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
# Normal distribution
# Go to http://dev.theomader.com/gaussian-kernel-calculator/, enter sigma=1.5, size=13 (so that it will max on 1.5-1 gap)
# Weights: 0.000116 0.001227 0.008466 0.037976 0.110867 0.210789 0.261121 0.210789 0.110867 0.037976 0.008466 0.001227 0.000116
# Correspond to the gaps between:
#          4.5-4    4-3.5    3.5-3    3-2.5    2.5-2    2-1.5    1.5-1    1-0.5    0.5-0    Not Used-->
# So we have: 0.000116 0.001227 0.008466 0.037976 0.110867 0.210789 0.261121 0.210789 0.110867
# Sum = 0.952218, so multiply by 1/0.952218=1.050179 to get sum of 1
# Now: 1.21820764e-04, 1.28856963e-03, 8.89081541e-03, 3.98815977e-02, 1.16430195e-01, 2.21366181e-01, 2.74223791e-01, 2.21366181e-01, 1.16430195e-01
# Finally, to preserve a max of 10 (which is a gap of 10/9=1.11111), we multiply by 10:
# 0.001218, 0.01289, 0.08891, 0.3988, 1.164, 2.214, 2.742, 2.214, 1.164
#     0.0    -   10.0
#     0.5    -   8.836
#     1.0    -   6.622
#     1.5    -   3.880
#     2.0    -   1.666
#     2.5    -   0.5018
#     3.0    -   0.1030
#     3.5    -   0.01411
#     4.0    -   0.001218
#     4.5    -   0.0
#
# SYSTEM = 3
# Manually changing points gaps to try and make it a good spread (aspacek)
#     0.0    -   10
#     0.5    -   8.5
#     1.0    -   6.5
#     1.5    -   4
#     2.0    -   2.5
#     2.5    -   1.5
#     3.0    -   1
#     3.5    -   0.5
#     4.0    -   0.25
#     4.5    -   0
#
# SYSTEM = 4
# /u/d_anda from reddit's recommended point spread
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
# SYSTEM = 5
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
# Function that computes the similarity score:
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
			0.0:10.0,
			0.5:8.836,
			1.0:6.622,
			1.5:3.880,
			2.0:1.666,
			2.5:0.5018,
			3.0:0.1030,
			3.5:0.01411,
			4.0:0.001218,
			4.5:0.0,
		}
		return switcher.get(diff,"Error in rating difference")
	elif system == '3':
		switcher={
			0.0:10,
			0.5:8.5,
			1.0:6.5,
			1.5:4,
			2.0:2.5,
			2.5:1.5,
			3.0:1,
			3.5:0.5,
			4.0:0.25,
			4.5:0,
		}
		return switcher.get(diff,"Error in rating difference")
	elif system == '4':
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
	elif system == '5':
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
print('\nNote: each user takes about 30 seconds to process.')
print('So, comparing two users takes about 1 minute.')
print('When comparing to following or followers, here are some estimations:')
print('10 users = 5 minutes')
print('100 users = 50 minutes')
print('1000 users = 8 hours')
print('\nSystems:')
print('1 = even difference points between 1 and 10')
print('2 = normal distribution in point differences with sigma=1.5 peaking on difference between 1 and 1.5')
print('3 = manual distribition in point differences by aspacek')
print('4 = manual distribution in point differences by /u/d_anda')
print('5 = max points start at 10 and then are halved for each larger difference')
starttime = datetime.datetime.now()
times = []

# The two users being compared, or if all friends are being compared:
user1 = "moogic" #input(f"\nLetterboxd Username 1:\n")
user2 = "blankments" #input(f"\nLetterboxd Username 2, or 'following' or 'followers':\n")
system = "5" #input(f"\nSystem:\n")

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
		print(user1+' ratings: '+str(oglength1))
		print(user2+' ratings: '+str(oglength2))
		print('matched films: '+str(len(finalfilms))+'\n')

		# Get the similarity score and print results:
		if len(finalfilms) > 0:
			results = scoring(finalfilms,finalratings1,finalratings2,system)
			print('RESULTS = '+str(results)+'\n')
		else:
			print('No film matches found.\n')
	else:
		print('No films to match.\n')

	# Print final timing:
	totaltime = datetime.datetime.now()-starttime
	print('Total time = '+str(totaltime)+'\n')

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
	tocompute = "10" #input(f"\nChoose a number to compute:\n")
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
	loopstarttime = datetime.datetime.now()
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
			print(user1+' ratings: '+str(oglength1))
			print(users[i]+' ratings: '+str(oglength2))
			print('matched films: '+str(len(finalfilms)))
			if len(finalfilms) > 0:
				print('compatibility: '+str(results))
			else:
				print('No film matches found.')
			elapsedtime = datetime.datetime.now()-starttime
			print('time elapsed = '+str(elapsedtime))
			loopelapsedtime = datetime.datetime.now()-loopstarttime
			timeperloop = loopelapsedtime/(i+1.0)
			estimatedtime = (len(users)-(i+1.0))*timeperloop
			times = times+[estimatedtime+elapsedtime]
			avgtime = sum(times,datetime.timedelta())/len(times)
			if i == len(users)-1:
				print('estimated time remaining = '+str(elapsedtime-elapsedtime)+'\n')
			else:
				print('estimated time remaining = '+str(avgtime-elapsedtime)+'\n')
		else:
			scores = scores+[-1]

	# Sort all the scores:
	sortedusers = [name for number,name in sorted(zip(scores,users))]
	sortedusers.reverse()
	scores.sort()
	scores.reverse()

	# Print out results:
	print('Comparing '+user1+' '+user2+'\n')
	for i in range(len(sortedusers)):
		print(sortedusers[i]+' -- '+str(scores[i]))

	# Print final timing:
	totaltime = str(datetime.datetime.now()-starttime)
	print('\nTotal time = '+totaltime+'\n')

	print(sortedusers)
	print(scores)
