import requests
import sys

########################
# The similarity system:
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
def similarity(i):
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
	return switcher.get(i,"Error in rating difference")

##############################################
# Function to grab a user's films and ratings:
def userfilms(user):

	# The base url of each user's film ratings:
	url = 'https://letterboxd.com/'+user+'/films/ratings/'
	# Grab source code for first ratings page:
	r = requests.get(url)
	source = r.text
	
	# Find the number of ratings pages:
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

	# Return the results
	return finalfilms,finalratings1,finalratings2

##############################################
# Function to compute final similarity scores:
def scoring(finalfilms,finalratings1,finalratings2):
	finalpoints = []
	for i in range(len(finalfilms)):
		diff = abs(int(finalratings1[i])-int(finalratings2[i]))/2.0
		points = similarity(diff)
		finalpoints = finalpoints+[points]
	result = sum(finalpoints)/len(finalpoints)
	return result

############################
#### START MAIN PROGRAM ####
############################

# Beginning text:
print('\nNote: each user takes about 30 seconds to process.')
print('So, comparing two users takes about 1 minute.')
print('When comparing to following or followers, here are some estimations:')
print('10 users = 5 minutes')
print('100 users = 50 minutes')
print('1000 users = 8 hours')

# The two users being compared, or if all friends are being compared:
user1 = input(f"\nLetterboxd Username 1:\n")
user2 = input(f"\nLetterboxd Username 2, or 'following' or 'followers':\n")

# If just two users are being compared:
if user2 != 'following' and user2 != 'followers':
	print('\nThe users being compared are '+user1+' and '+user2+'\n')
	
	# Working on user1:
	print('Grabbing all film ratings from '+user1+'\n')
	films1,ratings1 = userfilms(user1)
	
	# Working on user2:
	print('Grabbing all film ratings from '+user2+'\n')
	films2,ratings2 = userfilms(user2)
	
	# Find all matching films:
	print('Finding matching films\n')
	oglength1 = len(films1)
	oglength2 = len(films2)
	finalfilms,finalratings1,finalratings2 = filmmatch(films1,ratings1,films2,ratings2)
	print(user1+' ratings: '+str(oglength1))
	print(user2+' ratings: '+str(oglength2))
	print('matched films: '+str(len(finalfilms))+'\n')

	# Get the similarity score and print results:
	results = scoring(finalfilms,finalratings1,finalratings2)
	print('RESULTS = '+str(results)+'\n')

# Else go through following or followers
else:

	# Find all following or followers:
	if user2 == 'following':
		print('\nGrabbing all users that '+user1+' is following\n')
	else:
		print('\nGrabbing all users that follow '+user1+'\n')
	users = userfollow(user1,user2)

	# Compute similarity score for all users:
	# Just need to grab films for user1 once:
	print('Grabbing all film ratings from '+user1+'\n')
	films1,ratings1 = userfilms(user1)
	# Initialize results:
	scores = []
	for i in range(len(users)):
		print('Comparing with '+users[i]+' ('+str(i+1)+'/'+str(len(users))+')')
		films2,ratings2 = userfilms(users[i])
		finalfilms,finalratings1,finalratings2 = filmmatch(films1,ratings1,films2,ratings2)
		print(len(finalfilms))
		results = scoring(finalfilms,finalratings1,finalratings2)
		scores = scores+[results]

	# Sort all the scores:
	sortedusers = [name for number,name in sorted(zip(scores,users))]
	sortedusers.reverse()
	scores.sort()
	scores.reverse()

	# Print out results:
	print('Comparing '+user1+' '+user2+'\n')
	for i in range(len(users)):
		print(users[i]+' -- '+str(scores[i]))
