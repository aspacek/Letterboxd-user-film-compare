#!/bin/bash

# Running multiple runs of the program with different inputs:

# moogic - following - system 1 - useratings - all
python user_film_compare.py full_input.txt 0

# system 2
sed -i.bak -e 's/system = 1/#system = 1/g' full_input.txt
sed -i.bak -e 's/#system = 2/system = 2/g' full_input.txt
python user_film_compare.py full_input.txt 0

# system 3
sed -i.bak -e 's/system = 2/#system = 2/g' full_input.txt
sed -i.bak -e 's/#system = 3/system = 3/g' full_input.txt
python user_film_compare.py full_input.txt 0

# followers - system 1
sed -i.bak -e 's/user2 = following/#user2 = following/g' full_input.txt
sed -i.bak -e 's/#user2 = followers/user2 = followers/g' full_input.txt
sed -i.bak -e 's/system = 3/#system = 3/g' full_input.txt
sed -i.bak -e 's/#system = 1/system = 1/g' full_input.txt
python user_film_compare.py full_input.txt 0

# system 2
sed -i.bak -e 's/system = 1/#system = 1/g' full_input.txt
sed -i.bak -e 's/#system = 2/system = 2/g' full_input.txt
python user_film_compare.py full_input.txt 0

# system 3
sed -i.bak -e 's/system = 2/#system = 2/g' full_input.txt
sed -i.bak -e 's/#system = 3/system = 3/g' full_input.txt
python user_film_compare.py full_input.txt 0

rm full_input.txt.bak
