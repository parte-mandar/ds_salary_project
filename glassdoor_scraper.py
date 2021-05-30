from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
import pandas as pd

# Currect page number
page_number = 0

# For tracking jobs visited
job_id = ""
job_id_list = []

def get_last_job_id_int():
    a = 0
    incr = 0
    temp_str = ""
    for a in job_id_list[-1]:
        if incr >=2:
            temp_str = temp_str + a
        
        incr = incr + 1
        
    return int(temp_str)

def increment_page_number():
    global page_number
    page_number = page_number + 1
    
def get_page_number():
    return page_number

# This function is useful if you have weak internet connection.
# If you have to get big data of say 1000 jobs, run this.
# It will divide and create seperate csv files for 100 jobs each time.
# This is so that if the network failed on say 550th job, then you still have 5 csv files of 500 unique jobs which you can merge later.
# If you have a good connection, run get_jobs() directly
def get_jobs_in_chunk(keyword, df_path, num_jobs, verbose, path, slp_time, chunk_size = 0, chunked = True):
    job_chunk = 0
    incr = 0
    while num_jobs > 0:
        if(num_jobs >= chunk_size):
            job_chunk = chunk_size
            num_jobs = num_jobs - chunk_size
        else:
            job_chunk = num_jobs
            num_jobs = 0
            
        # page = get_page_number()
        # last_job_id = get_last_job_id()
        
        # Get jobs in chunk    
        df = get_jobs(keyword, job_chunk, verbose, path, slp_time, chunked)
        if not df.empty:
            incr = incr + 1
            print("Chunk " + str(incr) + " Saved")
            df.to_csv(df_path + "glassdoor_jobs_set_" + str(incr) + ".csv", index=False)
        

def get_jobs(keyword, df_path, num_jobs, verbose, path, slp_time, chunked = False): # , chunk_size = 0
    
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    
    #Initializing the webdriver
    options = webdriver.ChromeOptions()
    
    #Uncomment the line below if you'd like to scrape without a new Chrome window every time.
    #options.add_argument('headless')
    
    #Change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.set_window_size(1000, 800)
    
    #url = 'https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword="' + keyword + '"&sc.keyword="'+ keyword +'"&locT=C&locId=1147401'
    
    url = 'https://www.glassdoor.com/Job/jobs.htm?sc.generalKeyword="'+ keyword +'"&includeNoSalaryJobs=false'
    # url = 'https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=%22' + keyword + '%22&sc.keyword=%22' + keyword + '%22&locT=C&locId=1147401&jobType='
    # &locT=C&locId=1147401&locKeyword=San%20Francisco,%20CA&jobType=all&fromAge=-1&minSalary=0&includeNoSalaryJobs=false&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0'
    driver.get(url)
    
    jobs = [] # All error free job postings will end up here.
    no_job = False # If something went wrong with any job posting, this will turn true and that job will be ignored.
    count_recorded_jobs = 0 # Total number of jobs encountered, only job without errors will end up in the dataset.
    count_successful_jobs = 0 # Successful jobs in a weblist
    job_number = 0 # Current job number, according to the page.
    rechecking = False # If the list is rechecked.
    existing = False # To check if an Job id is already in the list.
    unprocessed_jobs_on_page = 0 # Unprocessed due to some reason in the weblist.

    while len(jobs) < num_jobs:  #If true, should be still looking for new jobs.
    
        rechecking = False
        existing = False
        
        #Clicking on the "next page" button
        try:                
            # driver.find_element_by_xpath('.//li[@class="next"]//a').click()
            driver.find_element_by_xpath('//*[@id="FooterPageNav"]//a[@data-test="pagination-next"]').click()
            
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs)))
            break
        
        
        # IDs recorded from last page
        for job_check in job_id_list[-count_successful_jobs:]:
            print(job_check)
        
        
        # If there are too many failed job postings in the page, process the page back
        if unprocessed_jobs_on_page >= 15: 
            rechecking = True
            print("\nToo many unprocessed jobs, Rechecking the same Page")
            time.sleep(slp_time) # Wait for the page to load
            try:                
                # driver.find_element_by_xpath('.//li[@class="next"]//a').click()
                driver.find_element_by_xpath('//*[@id="FooterPageNav"]//a[@data-test="pagination-prev"]').click()
            
            except NoSuchElementException:
                print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs)))
                break
        
        #Let the page load. Change this number based on your internet speed.
        #Or, wait until the webpage is loaded, instead of hardcoding it.
        time.sleep(slp_time)

        #Test for the "Sign Up" prompt and get rid of it.
        # try:
        #     driver.find_element_by_class_name("selected").click()
        # except ElementClickInterceptedException:
        #     pass

        # time.sleep(.1)

        #try:
        #    driver.find_element_by_class_name("ModalStyle__xBtn___29PT9").click()  #clicking to the X.
        #    print("Success")
        #except NoSuchElementException:
        #    pass
        
        currentJoblist = 0
        
        if not (len(jobs) >= num_jobs):
            no_job = False
            existing = False
            
            print("\n---Complete Details---\nCurrent Jobs in the list: {} \nJobs processed: {} \nJobs not processed: {}".format(len(jobs), count_recorded_jobs, count_recorded_jobs-len(jobs)))
            print("\n---Page {} Details---\nJobs successfully in the list: {} \nJobs processed: {} \nJobs not processed on this page: {}".format(page_number, count_successful_jobs, job_number, unprocessed_jobs_on_page))
            print("\n")
            listButtonsCount = len(driver.find_elements_by_xpath('//*[@id="MainCol"]//div[1]//ul//li[@data-test="jobListing"]'))
            #listButtonsCount = 10
            
            job_number = 0
            unprocessed_jobs_on_page = 0
            
            if not rechecking:
                count_successful_jobs = 0
                increment_page_number()
                
            if rechecking:
                print(">>>>>>Rechecking<<<<<")
            
            print("Page number: {}".format(page_number))
            print("Job buttons: {}".format(str(listButtonsCount)))
            
            #Going through each job in this page
            try:
                job_buttons = driver.find_elements_by_xpath('.//*[@id="MainCol"]//a[@class="jobLink"]')  #jl for Job Listing. These are the buttons we're going to click.
            except:
                print("Not Found!")
            
            for job_button in job_buttons:  
                no_job = False
                existing = False
                job_number = job_number + 1
                
                print("------Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))
                if len(jobs) >= num_jobs:
                    print("Completed!")
                    break
                
                try:
                    job_button.click()  #You might 
                except:
                    no_job = True    
                    unprocessed_jobs_on_page = unprocessed_jobs_on_page + 1
                    print("Job button not clickable or not found!")
                
                
                time.sleep(10)
                
                #___________ code to kill the sign-up pop-up after it render on screen
                try:
                    driver.find_element_by_css_selector('[alt="Close"]').click()
                    # print("&&& line 89")
                    # found_popup = True
                    print("Closed an appeared popup on the website")
                    no_job = True
                except NoSuchElementException:
                    # print("&&& line 92")
                    pass
                          
                # __________
                
                
                collected_successfully = False
                
                while not collected_successfully:
                    try:
                        # company_name = driver.find_element_by_xpath('.//div[@class="employerName"]').text
                        company_name = driver.find_element_by_xpath('//*[@id="MainCol"]//li['+ str(currentJoblist + 1) +']//div[2]//a//span').text
                        
                        # location = driver.find_element_by_xpath('.//div[@class="location"]').text
                        location = driver.find_element_by_xpath('//*[@id="MainCol"]//li['+ str(currentJoblist + 1) +']//div[2]//div[2]/span').text
                        
                        # job_title = driver.find_element_by_xpath('.//div[contains(@class, "title")]').text
                        job_title = driver.find_element_by_xpath('//*[@id="MainCol"]//li['+ str(currentJoblist + 1) +']//a[@data-test="job-link"]').text
                        
                        job_description = driver.find_element_by_xpath('.//div[@class="jobDescriptionContent desc"]').text
                        
                        # job_function is an additional information not included in previous code
                        # job_function = driver.find_element_by_xpath('//*[@id="JDCol"]//strong[text()[1]="Job Function"]//following-sibling::*').text
                        
                        collected_successfully = True
                        # print("success")
                    except:
                        # print("&&& line 67")
                        # collected_successfully=True
                        time.sleep(5)
    
                if not no_job:    
                    try:
                        # salary_estimate = driver.find_element_by_xpath('.//span[@class="gray small salary"]').text
                        salary_estimate = driver.find_element_by_xpath('//*[@id="JDCol"]//span[@data-test="detailSalary"]').text
                    except NoSuchElementException:
                        salary_estimate = -1 #You need to set a "not found value. It's important."
                        # salary_estimate = "No salary estimates found"
                        unprocessed_jobs_on_page = unprocessed_jobs_on_page + 1
                        print("No salary estimates found, Element Failed, Skipping!")
                        no_job = True # In this case, I want to work with salaries, so the jobs which has no salary estimate is of no use.
                
                try:
                    # rating = driver.find_element_by_xpath('.//span[@class="rating"]').text
                    rating = driver.find_element_by_xpath('//*[@id="JDCol"]//span[@data-test="detailRating"]').text
                except NoSuchElementException:
                    rating = -1 #You need to set a "not found value. It's important."
    
                # #Printing for debugging
                if verbose:
                    print("Job Title: {}".format(job_title))
                    print("Salary Estimate: {}".format(salary_estimate))
                    print("Job Description: {}".format(job_description[:500]))
                    print("Rating: {}".format(rating))
                    print("Company Name: {}".format(company_name))
                    print("Location: {}".format(location))
                    # print("Job Function: {}".format(job_function))
    
                #Going to the Company tab...
                #clicking on this:
                #<div class="tab" data-tab-type="overview"><span>Company</span></div>
                time.sleep(1)
                # driver.find_element_by_xpath('.//div[@class="tab" and @data-tab-type="overview"]').click()
                try_counter = 1
                if not no_job:
                    try:
                        driver.find_element_by_xpath('.//div[@id="SerpFixedHeader"]//span[text()="Company"]').click()
                        print('Element Found!')
                        try_counter = 0
                    except:
                        print("Job do not have a company tab, Element Failed, Skipping!")
                        no_job = True
                        unprocessed_jobs_on_page = unprocessed_jobs_on_page + 1
                        try_counter = 1
                    
                    #try:
                    #    <div class="infoEntity">
                    #    <label>Headquarters</label>
                    #    <span class="value">San Francisco, CA</span>
                    #    </div>
                    #    headquarters = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Headquarters"]//following-sibling::*').text
                    #    # ^^^^^^^^^^ couldn't abel to find "headquarters"
                    #except NoSuchElementException:
                    #    headquarters = -1
                
                if try_counter != 1:
                    try:
                        # size = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Size"]//following-sibling::*').text
                        size = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]//span[text()="Size"]//following-sibling::*').text
                    except NoSuchElementException:
                        size = -1
    
                    try:
                        # founded = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Founded"]//following-sibling::*').text
                        founded = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]//span[text()="Founded"]//following-sibling::*').text
                    except NoSuchElementException:
                        founded = -1
    
                    try:
                        # type_of_ownership = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Type"]//following-sibling::*').text
                        type_of_ownership = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]//span[text()="Type"]//following-sibling::*').text
                    except NoSuchElementException:
                        type_of_ownership = -1
    
                    try:
                        # industry = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Industry"]//following-sibling::*').text
                        industry = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]//span[text()="Industry"]//following-sibling::*').text
                    except NoSuchElementException:
                        industry = -1
    
                    try:
                        # sector = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Sector"]//following-sibling::*').text
                        sector = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]//span[text()="Sector"]//following-sibling::*').text
                    except NoSuchElementException:
                        sector = -1
    
                    try:
                        # revenue = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Revenue"]//following-sibling::*').text
                        revenue = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]//span[text()="Revenue"]//following-sibling::*').text
                    except NoSuchElementException:
                        revenue = -1
                    
                    #try:
                        #competitors = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Competitors"]//following-sibling::*').text
                        # ^^^^^^^^^^^ couldn't able to find "competitors"
                    #except NoSuchElementException:
                        #competitors = -1
                    
                if verbose:
                    
                    print("Size: {}".format(size))
                    print("Founded: {}".format(founded))
                    print("Type of Ownership: {}".format(type_of_ownership))
                    print("Industry: {}".format(industry))
                    print("Sector: {}".format(sector))
                    print("Revenue: {}".format(revenue))
                    # print("Headquarters: {}".format(headquarters))
                    # print("Competitors: {}".format(competitors))
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    
    
                count_recorded_jobs = count_recorded_jobs + 1 # Incrementing jobs processed so far
                if not no_job:
                    
                    job_id = "p" + str(page_number) + "j" + str(job_number)
                    if not rechecking:
                        count_successful_jobs = count_successful_jobs + 1
                        job_id_list.append(job_id)
                    else:
                        for job_check in job_id_list[-count_successful_jobs:]:
                            if job_check == job_id:
                                existing = True
                                print("The Job posting already exists, Skipped!")
                
                    if rechecking and not existing:
                        count_successful_jobs = count_successful_jobs + 1
                        job_id_list.append(job_id)
                
                    if not existing:
                        
                        print("Job successfully recorded: Job ID: {}".format(job_id))
                        
                        jobs.append({"Job ID" : job_id,
                        "Job Title" : job_title,           
                        "Salary Estimate" : salary_estimate,
                        "Job Description" : job_description,            
                        "Company Name" : company_name,
                        "Rating" : rating,            
                        "Location" : location,
                        "Size" : size,
                        "Founded" : founded,
                        "Type of ownership" : type_of_ownership,
                        "Industry" : industry,
                        "Sector" : sector,
                        "Revenue" : revenue})
                        # "Headquarters" : headquarters,
                        # "Job Function" : job_function,
                        # "Competitors" : competitors})
                        # ^^^^^^^^ couldn't able to find "Headquarters" and "Competitors"
                        #add job to jobs
    
                currentJoblist=currentJoblist+1 # increasing the count of the list of buttons clicked and saved
                
                #if chunked and chunk_counter == chunk_size:
                if chunked:    
                    df = pd.DataFrame(jobs)
                    if not df.empty:
                        print("DataFrame Saved")
                        #df.to_csv(df_path + "glassdoor_jobs_set_" + str(len(jobs) - chunk_size) + ".csv", index=False)
                        df.to_csv(df_path + "glassdoor_jobs_set.csv", index=False)
                        
                
                if not (currentJoblist < listButtonsCount): # to check the list last button and to go to next page
                        currentJoblist = 0  # resetting the button list count for new page button's list
                        break
