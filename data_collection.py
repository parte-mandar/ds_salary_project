#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 10:05:17 2021

@author: mandarparte
"""

import glassdoor_scraper as gs
import pandas as pd

path = "/home/mandarparte/Programs/Python/Data Science/ds_salary_project/chromedriver"

df = gs.get_jobs("Data Scientist", 15, False, path, 15)