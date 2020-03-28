# The point of this file is to remove any user input requests with given values.

# Read in main file:
infile = open("user_film_compare.py","r")
indata = infile.read()
# Get output file ready:
outfile = open("user_film_compare_CI.py","w")

# Add user names:
indata = indata.replace('user1 = input(f"\\nLetterboxd Username 1:\\n")','user1 = "moogic"')
indata = indata.replace('user2 = input(f"\\nLetterboxd Username 2, or \'following\' or \'followers\':\\n")','user2 = "blankments"')
indata = indata.replace('system = input(f"\\nSystem:\\n")','system = "5"')
indata = indata.replace('tocompute = input(f"\\nChoose a number to compute:\\n")','tocompute = "10"')

outfile.write(indata)

infile.close()
outfile.close()
