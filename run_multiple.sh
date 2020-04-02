#!/bin/bash

# Running multiple runs of the program with different inputs

# usage: >>bash run_multiple.sh

# Print out details? verbose = 1 (yes) or 0 (no)
verbose=0

# Copy input to use
cp full_input.txt input.txt

# moogic - following - system 1 - useratings - all
# (the "sed" commands are removing the comment ("#") symbol where appropriate)
sed -i.bak -e 's/#user1 = moogic/user1 = moogic/g' input.txt
sed -i.bak -e 's/#user2 = following/user2 = following/g' input.txt
sed -i.bak -e 's/#system = 1/system = 1/g' input.txt
sed -i.bak -e 's/#useratings = use/useratings = use/g' input.txt
sed -i.bak -e 's/#tocompute = all/tocompute = all/g' input.txt
sed -i.bak -e 's/#spreadchoice = y/spreadchoice = y/g' input.txt
sed -i.bak -e 's/#outtxtchoice = y/outtxtchoice = y/g' input.txt
sed -i.bak -e 's/#outcsvchoice = y/outcsvchoice = y/g' input.txt
python user_film_compare.py input.txt $verbose

# following - system 2
sed -i.bak -e 's/system = 1/#system = 1/g' input.txt
sed -i.bak -e 's/#system = 2/system = 2/g' input.txt
python user_film_compare.py input.txt $verbose

# following - system 3
sed -i.bak -e 's/system = 2/#system = 2/g' input.txt
sed -i.bak -e 's/#system = 3/system = 3/g' input.txt
python user_film_compare.py input.txt $verbose

# followers - system 1
sed -i.bak -e 's/user2 = following/#user2 = following/g' input.txt
sed -i.bak -e 's/#user2 = followers/user2 = followers/g' input.txt
sed -i.bak -e 's/system = 3/#system = 3/g' input.txt
sed -i.bak -e 's/#system = 1/system = 1/g' input.txt
python user_film_compare.py input.txt $verbose

# followers - system 2
sed -i.bak -e 's/system = 1/#system = 1/g' input.txt
sed -i.bak -e 's/#system = 2/system = 2/g' input.txt
python user_film_compare.py input.txt $verbose

# followers - system 3
sed -i.bak -e 's/system = 2/#system = 2/g' input.txt
sed -i.bak -e 's/#system = 3/system = 3/g' input.txt
python user_film_compare.py input.txt $verbose

# both - system 1
sed -i.bak -e 's/user2 = followers/#user2 = followers/g' input.txt
sed -i.bak -e 's/#user2 = both/user2 = both/g' input.txt
sed -i.bak -e 's/system = 3/#system = 3/g' input.txt
sed -i.bak -e 's/#system = 1/system = 1/g' input.txt
python user_film_compare.py input.txt $verbose

# both - system 2
sed -i.bak -e 's/system = 1/#system = 1/g' input.txt
sed -i.bak -e 's/#system = 2/system = 2/g' input.txt
python user_film_compare.py input.txt $verbose

# both - system 3
sed -i.bak -e 's/system = 2/#system = 2/g' input.txt
sed -i.bak -e 's/#system = 3/system = 3/g' input.txt
python user_film_compare.py input.txt $verbose

# Remove the backup file created by the "sed" commands
rm input.txt.bak
