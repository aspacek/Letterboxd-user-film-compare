import csv
import sys

# This file checks all of the results from the CI file outputs

# Function to do all the value checking:
def valcheck(messages,which,type,name,constraint,input):	
	# which = 'user_user_1'
	# type = 'min', 'val', 'minmax'
	# name = 'rating', 'rating1', 'rating2', 'match', 'result', 'time'
	# constraint = single number for 'min' or 'val'
	#              2-element array for 'minmax'

	# Tolerances, in percents:
	ratingtolerance = 0.2
	matchtolerance = 0.2
	resulttolerance = 0.2

	# Check which tolerance to use:
	if name == 'rating' or name == 'rating1' or name == 'rating2':
		tolerance = ratingtolerance
	elif name == 'match':
		tolerance = matchtolerance
	elif name == 'result':
		tolerance = resulttolerance
	elif name == 'time':
		tolerance = -1

	# Go through the different types:
	allpass = 1
	if type == 'min':
		if input < constraint:
			allpass = 0
			messages = messages+['ERROR - '+which+' - '+name+' too low']
		elif input > constraint+constraint*tolerance:
			allpass = 0
			messages = messages+['ERROR - '+which+' - '+name+' too high']
	elif type == 'val':
		if input < constraint-constraint*tolerance:
			allpass = 0
			messages = messages+['ERROR - '+which+' - '+name+' too low']
		elif input > constraint+constraint*tolerance:
			allpass = 0
			messages = messages+['ERROR - '+which+' - '+name+' too high']
	elif type == 'minmax':
		if input < constraint[0]:
			allpass = 0
			messages = messages+['ERROR - '+which+' - '+name+' is less than '+str(constraint[0])+' seconds']
		elif input > constraint[1]:
			allpass = 0
			messages = messages+['ERROR - '+which+' - '+name+' is greater than '+str(constraint[1])+' seconds']
	if allpass == 1:
		messages = messages+['PASS  - '+which+' - '+name]
	return messages

##################
# BEGIN THE CHECKS
##################

# Save pass/fail messages for output:
messages = []

# user_user_1 check
user1min = 833
user2min = 1325
matchedmin = 184
resultsval = 7.984
timemin = 0.1
timemax = 120.0
with open('CI/user_film_compare_CI_user_user_1.txt') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=' ')
	count = 0
	for row in csv_reader:
		if count == 0:
			user1ratings = row[2]
		elif count == 1:
			user2ratings = row[2]
		elif count == 2:
			matched = row[2]
		elif count == 3:
			results = row[2]
		elif count == 4:
			totaltime = row[4]
		count = count+1
messages = valcheck(messages,'user_user_1','min','rating1',user1min,int(user1ratings))
messages = valcheck(messages,'user_user_1','min','rating2',user2min,int(user2ratings))
messages = valcheck(messages,'user_user_1','min','match',matchedmin,int(matched))
messages = valcheck(messages,'user_user_1','val','result',resultsval,float(results))
messages = valcheck(messages,'user_user_1','minmax','time',[timemin,timemax],float(totaltime))

# user_user_2 check
user1min = 833
user2min = 1325
matchedmin = 184
resultsval = 6.677
timemin = 0.1
timemax = 120.0
with open('CI/user_film_compare_CI_user_user_2.txt') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=' ')
	count = 0
	for row in csv_reader:
		if count == 0:
			user1ratings = row[2]
		elif count == 1:
			user2ratings = row[2]
		elif count == 2:
			matched = row[2]
		elif count == 3:
			results = row[2]
		elif count == 4:
			totaltime = row[4]
		count = count+1
messages = valcheck(messages,'user_user_2','min','rating1',user1min,int(user1ratings))
messages = valcheck(messages,'user_user_2','min','rating2',user2min,int(user2ratings))
messages = valcheck(messages,'user_user_2','min','match',matchedmin,int(matched))
messages = valcheck(messages,'user_user_2','val','result',resultsval,float(results))
messages = valcheck(messages,'user_user_2','minmax','time',[timemin,timemax],float(totaltime))

# user_user_3 check
user1min = 833
user2min = 1325
matchedmin = 184
resultsval = 5.698
timemin = 0.1
timemax = 120.0
with open('CI/user_film_compare_CI_user_user_3.txt') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=' ')
	count = 0
	for row in csv_reader:
		if count == 0:
			user1ratings = row[2]
		elif count == 1:
			user2ratings = row[2]
		elif count == 2:
			matched = row[2]
		elif count == 3:
			results = row[2]
		elif count == 4:
			totaltime = row[4]
		count = count+1
messages = valcheck(messages,'user_user_3','min','rating1',user1min,int(user1ratings))
messages = valcheck(messages,'user_user_3','min','rating2',user2min,int(user2ratings))
messages = valcheck(messages,'user_user_3','min','match',matchedmin,int(matched))
messages = valcheck(messages,'user_user_3','val','result',resultsval,float(results))
messages = valcheck(messages,'user_user_3','minmax','time',[timemin,timemax],float(totaltime))

# Print message to screen and to an output to a file:
for i in range(len(messages)):
	print(messages[i])
outfile = open('CI/user_film_compare_results.txt','w')
for i in range(len(messages)):
	outfile.write(messages[i]+'\n')
# Close output file:
outfile.close()
