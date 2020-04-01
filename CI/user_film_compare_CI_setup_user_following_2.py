# TESTING User to Following Comparison

# moogic and following

# system = 2

# The point of this file is to remove any user input requests with given values.

# Read in main file:
infile = open("user_film_compare.py","r")
indata = infile.read()
# Get output file ready:
outfile = open("CI/user_film_compare_CI_user_following_2.py","w")

# Add user names:
indata = indata.replace('user1 = input(f"\\nLetterboxd Username 1:\\n")','user1 = "moogic"')
indata = indata.replace('user2 = input(f"\\nLetterboxd Username 2, or \'following\' or \'followers\':\\n")','user2 = "following"')

# Add system choice:
indata = indata.replace('system = input(f"\\nSystem:\\n")','system = "2"')

# Use available ratings if they exist:
indata = indata.replace('useratings = input(f"\\nUse saved rating if available, or get all new ratings? (use/new)\\n")','useratings = "use"')

# Add number to compute:
indata = indata.replace('tocompute = input(f"\\nChoose a number to compute:\\n")','tocompute = "3"')

# Don't overwrite spread or output text and CSV data:
indata = indata.replace('spreadchoice = input(f"\\nCompute new spread and overwrite the previous? (y/n):\\n")','spreadchoice = "n"')
indata = indata.replace('outtxtchoice = input(f"\\nOverwrite the previous text output? (y/n):\\n")','outtxtchoice = "n"')
indata = indata.replace('outcsvchoice = input(f"\\nOverwrite the previous CSV output? (y/n):\\n")','outcsvchoice = "n"')

# Write out results to a file to be checked:
indata = indata.replace("outpathtxt = Path('Output/'+user1+'_'+user2+'_output.txt')","outpathtxt = Path('trash')")
indata = indata.replace("outpathcsv = Path('Output/'+user1+'_'+user2+'_output.csv')","outpathcsv = Path('trash')")
indata = indata.replace("outfile = open('Output/'+user1+'_'+user2+'_output.txt','w')","outfile = open('CI/user_film_compare_CI_user_following_2.txt','w')")
indata = indata.replace("with open('Output/'+user1+'_'+user2+'_output.csv', mode='w') as outfile:","with open('CI/user_film_compare_CI_user_following_2.csv', mode='w') as outfile:")

# Ignore user vs user output writing:
indata = indata.replace("print('{:{longest}} {:d}'.format(user1+' ratings:',oglength1,longest=longest))","trash = -1",1)
indata = indata.replace("print('{:{longest}} {:d}'.format(user2+' ratings:',oglength2,longest=longest))","trash = -1")
indata = indata.replace("print('{:{longest}} {:d}{}'.format('matched films:',len(finalfilms),'\\n',longest=longest))","trash = -1")
indata = indata.replace("print('RESULTS = {:.3f}{}'.format(results,'\\n'))","trash = -1")
indata = indata.replace("print('Total time (s) = {:.3f}{}'.format(totaltime,'\\n'))","trash = -1")

# Remove all printing, replacing with "trash = -1" when it's the only thing after an if/else statement:
indata = indata.replace("print('No film matches found.\\n')","trash = -1")
indata = indata.replace("print('No films to match.\\n')","trash = -1")
indata = indata.replace("print('\\nGrabbing all users that '+user1+' is following\\n')","trash = -1")
indata = indata.replace("print('\\nGrabbing all users that follow '+user1+'\\n')","trash = -1")
indata = indata.replace("print('compatibility: {:.5f}'.format(results))","trash = -1")
indata = indata.replace("print('No film matches found.')","trash = -1")
indata = indata.replace("print('estimated time remaining (m) = {:.3f}{}'.format(0.0,'\\n'))","trash = -1")
indata = indata.replace("print('estimated time remaining (m) = {:.3f}{}'.format((avgtime-elapsedtime)/60.0,'\\n'))","trash = -1")
indata = indata.replace("print('{:{longest}} -- {:8.5f} -- {}'.format(sortedusers[i],scores[i],sortedinterpretations[i],longest=longest))","trash = -1")
indata = indata.replace('print','#print')

outfile.write(indata)

infile.close()
outfile.close()
