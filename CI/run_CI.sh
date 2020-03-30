#!/bin/bash

# Running all CI files:

python CI/user_film_compare_CI_setup_user_user_1.py
python CI/user_film_compare_CI_setup_user_user_2.py
python CI/user_film_compare_CI_setup_user_user_3.py

python CI/user_film_compare_CI_user_user_1.py
python CI/user_film_compare_CI_user_user_2.py
python CI/user_film_compare_CI_user_user_3.py

# Checking results:
python CI/user_film_compare_results_check.py
