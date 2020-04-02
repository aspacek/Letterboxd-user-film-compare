# Letterboxd-user-film-compare

<p align="left">
  <a href="https://github.com/aspacek/Letterboxd-user-film-compare"><img alt="GitHub aspacek status" src="https://github.com/aspacek/Letterboxd-user-film-compare/workflows/CI/badge.svg"></a>
</p>

This Python program is a project attempting to compare user film ratings on Letterboxd to determine how "similar" two users are. It has two modes of running:

- Comparing two given users to each other
- Comparing a given user with either the people they are following, or the people following them

To run, you need the file "user_film_compare.py" and an input file.
You also add verbose = 0 for no print out, or verbose = 1 for printing out details.

For example:

`python user_film_compare.py input.txt 1`

For an input file called "input.txt" and verbose = 1.

Written using python 3.7.

Tested successfully on python 3.6, 3.7, 3.8

(Python 3.5 seems to fail because of a problem with importing matplotlib.)

