#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 10:05:17 2021

@author: mandarparte
"""

import glassdoor_scraper as gs
import pandas as pd

# path = "/home/mandarparte/Programs/Python/Data Science/ds_salary_project/chromedriver"

# I'm using a different chrome driver path as I have shifted from Linux to Windows.
path = "F:/Programming/Python/chromedriver.exe"
df_path = "../Datasets/Glassdoor/"

# For stable internet connection
# get_jobs(keyword, df_path, num_jobs, verbose, path, slp_time, chunked = False):
gs.get_jobs("Data Scientist", df_path, 1000, False, path, 15, True)

#df.to_csv("../Datasets/test/glassdoor_jobs_test_10.csv", index=False)

# For unstable internet
#gs.get_jobs_in_chunk("Data Scientist", df_path, 50, False, path, 15, 10)

print(gs.get_page_number())
print(gs.get_last_job_id_int())
