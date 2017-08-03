'''
Created on May 14, 2017

@author: Choony
'''
import scrapy
import csv
import urllib2
import pprint
import openpyxl 
import StringIO
import re
import json
import time
import pickle
import logging
import datetime


from itertools import islice
from DataType.iPolyCourse import iPolyCourse
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

'''
Initial Crawler to extract SP's course data from mobile version
'''
SP_MobileDict = {}
Spider1Completed = False
class SP_MobileSpider(scrapy.Spider):
    name = "SP_MobileSpider"
    
    def start_requests(self):
        urls = ['http://m.sp.edu.sg/courses']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        global SP_MoblieDict
        coursePattern = re.compile("^([A-Z]{1}[0-9]{2})$")  # Match Alphabet + 2 Digits
        Results = response.xpath('//a[@class="courses-box-1"]/@href').extract()
        for rows in Results:
            courseID = "S" + rows[-2:]
            if (coursePattern.match(courseID)):
                SP_MobileDict[str(courseID)] =   str("http://m.sp.edu.sg/" + rows)
                
    def closed(self, reason):
        global Spider1Completed
        Spider1Completed = True
                
                    
class PolySpider(scrapy.Spider):
    
    name = "PolyIntake"
    intakeDict = {}
    courseList = []     # Contains list of all courses, be populated at the end by merging the ones below
    courseNPList = []   # List of NP course to be populated
    courseSPList = []   # List of SP course to be populated
    courseRPList = []   # List of RP course to be populated
    courseNYPList = []  # List of NYP course to be populated
    courseTPList = []   # List of TP course to be populated
    spCourseURL = {}
    courseURL = []
    intakeURL = []
    
    # Process Intake URL
    url_RPIntake = 'http://www.rp.edu.sg/Admissions_Information/Admissions/Planned_Intake_Figures.aspx'
    url_SPIntake = 'http://www.sp.edu.sg/wps/portal/vp-spws/spws.fsu.courseintakesandcut-offpoints'
    url_TPIntake = 'http://www.tp.edu.sg/admissions/course-intake-and-last-aggregate-scores'
    url_NPIntake = 'http://www.np.edu.sg/admissions/before-apply/Pages/courses.aspx'
    xls_NYP = 'http://www.nyp.edu.sg/content/dam/nyp/admissions/full-time-diploma/admission-exercise/intake-and-jae-elr2b2-points/2017-intake-and-2016-elr2b2.xlsx'
    intakeURL = [
        url_RPIntake,
        url_SPIntake,
        url_TPIntake,
        url_NPIntake,
        xls_NYP
        ]
    
    def __init__(self):
        self.driver = webdriver.Firefox()
    
    def start_requests(self):
        global SP_MobileDict
        global Spider1Completed
        
        while (not Spider1Completed):
            print "Waiting for SP Mobile Crawler..."
            time.sleep(1) # Wait for initial crawler to populate SP's mobile websites first
        
        self.spCourseURL = SP_MobileDict
            
        # Read all info from polytechnic.edu.sg's CSV file and populate whatever we can into courseList objects first.
        url_AllCourse = 'http://www.polytechnic.edu.sg/api/download/course?id=b434281c-efe6-69f6-9162-ff000003a8ed'
        cr = csv.reader(urllib2.urlopen(url_AllCourse))
        for row in islice(cr, 1, None): # Skip first item
            url = row[7]
            if (url[0] == "#"): # Some records have trailing # character, dont know why
                url = url[1:]
            if (url[-1] == "#"):
                url = url[:-1]
            courseObj = iPolyCourse(row[2], row[1], row[5], row[3], url, row[6], row[4])
            self.courseList.append(courseObj)
            
            if (url.startswith("http://www.np.edu.sg")):
                # Create mobile version of URL
                url2 = url.lower()
                mobile_Ext = url2[url2.find("courses")+8:url2.find("/pages")]
                if (mobile_Ext.find("fulltime") != -1):
                    mobile_Ext = mobile_Ext[len("fulltime/"):]
                if (mobile_Ext.find("diploma") != -1):
                    mobile_Ext = url2[url2.find("pages")+6:-5]
                
                mobile_Ext = "https://www1.np.edu.sg/eae/courses/" + mobile_Ext + "/"
                courseObj.setURL2(mobile_Ext)
                    
                self.courseNPList.append(courseObj)
                self.courseURL.append(mobile_Ext)
            elif (url.startswith("http://www.nyp.edu.sg")):
                self.courseNYPList.append(courseObj)
            elif (url.startswith("http://www.tp.edu.sg")):
                self.courseTPList.append(courseObj)
            elif (url.startswith("http://www.rp.edu.sg/")):
                self.courseRPList.append(courseObj)   
            elif (url.startswith("http://www.sp.edu.sg")):
                try:
                    self.courseURL.append(self.spCourseURL[row[2]])
                    courseObj.setURL2(self.spCourseURL[row[2]])
                    self.courseSPList.append(courseObj)
                except KeyError:
                    print "Course ID: " + row[2] + " not found!"
            
            self.courseURL.append(url)
                    
        for url in self.intakeURL:
            yield scrapy.Request(url=url, callback=self.parse)
        for url in self.courseURL:
            yield scrapy.Request(url=url, callback=self.parse)
    #END of start_requests()

    def parse(self, response):
        
        if response.url in self.intakeURL:
            self.processIntakeInfo(response)
        else:
            if (response.url.startswith("http://www.nyp.edu.sg/schools/")):
                self.driver.get(response.url)
                counter = 2 # Click start from year 2
                try:
                    while True: # Click all tabs that exist in NYP Course pages
                        element_present = EC.presence_of_element_located((By.ID, 'main_bg')) # Wait for the page to load
                        WebDriverWait(self.driver, 5).until(element_present) # 5 secs timeout
                        try:
                            self.driver.find_element_by_xpath('(//div[@class="panel-heading accordionPanelHeader"])[' + str(counter) + ']').click()
                            counter +=1
                            time.sleep(1)
                        except NoSuchElementException:
                            break
                    response = response.replace(body=self.driver.page_source)
                except TimeoutException:
                    print "Timed out waiting for page to load: " + response.url
            self.processCourseInfo(response)        
    #END of parse()
    
    def processIntakeInfo(self, response):
        coursePattern = re.compile("^([A-Z]{1}[0-9]{2})$")  # Match Alphabet + 2 Digits
        intakePattern = re.compile("^([0-9]{1,3})$")  # 1-3 Digits
        
        # Republic Poly Intake URL Crawler
        if (response.url == self.url_RPIntake):
            RPResults = response.xpath("//div[@class='content']//tr//td[not(contains(@bgcolor, '#6fb01e')) and contains(@align, 'center')]//text()").extract()
            i = 0
            while i < len(RPResults): # Returns a 1D-Arry of Course ID + Intake Size, parse 2 by 2
                self.intakeDict[RPResults[i].strip()] = RPResults[i+1].strip()
                i+=2  
                
        # Singapore Poly Intake URL Crawler
        elif (response.url == self.url_SPIntake):
            SPResults = response.xpath("//table[@id='tableDetails']//tr[not(contains(@class, 'yellow'))]//td//text()").extract()
            i = 0
            while i < len(SPResults): # Returns a 1D-Arry of Course Name (ID) + Intake Size + Score, parse 3 by 3
                courseID = SPResults[i]
                courseID = str(courseID[courseID.find("(")+len("("):courseID.rfind(")")].strip())
                courseIntake = str(SPResults[i+1].strip())
                self.intakeDict[courseID] = courseIntake
                i+=3
            
        # Temasek Poly Intake URL Crawler
        elif (response.url == self.url_TPIntake):
            TPResults = response.xpath(".//table[@class='table table-bordered']//tbody")
            for rows in TPResults.xpath(".//tr[not(contains(@class, 'info bold'))]"):
                courseID = str(rows.xpath(".//td[(contains(@class, 'subheaderleft'))]//text()").extract()[0].strip())
                courseIntake = str(rows.xpath(".//td[(contains(@class, 'intakeno'))]//text()").extract()[0].strip())
                if (coursePattern.match(courseID) and intakePattern.match(courseIntake)):
                    self.intakeDict[courseID] = courseIntake
        
        # Ngee Ann Poly Intake URL Crawler
        elif (response.url == self.url_NPIntake):
            NPResults = response.xpath(".//div[@class='ContentLeftHolder']//table[@border='1']")
            for rows in NPResults.xpath(".//tr[not(contains(@style, 'height:30pt'))]"):
                # NP tables got some entries that have weird char &#38203 taking up the first array or appending into the Course ID, so we always take last array (-1) and substring from char N
                courseID = rows.xpath(".//td[(contains(@width, '120'))]//text()").extract()[-1].encode('utf-8').strip()
                courseID = str(courseID[courseID.find("N"):])
                # Course Intake value will also have funny character, check if its digit, else index out for substring
                courseIntake = rows.xpath(".//td[(contains(@class, 'endcell'))]//text()").extract()[0].strip()
                
                i = 0;
                for c in courseIntake: 
                    if (c.isdigit() == False):
                        i+=1
                courseIntake = str(courseIntake[i:])
                if (coursePattern.match(courseID) and intakePattern.match(courseIntake)):
                    self.intakeDict[courseID] = courseIntake

        # Nanyang Poly Intake Crawler (Crawl by Excel file cause the school is fcking retarded to put up on website)
        elif (response.url == self.xls_NYP):   
            rawFile = urllib2.urlopen(self.xls_NYP).read()
            wb = openpyxl.load_workbook(StringIO.StringIO(rawFile), True)
            sheet = wb.worksheets[0]
            for i in range(1, sheet.max_row):
                courseID = str(sheet['B' + str(i)].value)
                courseIntake = str(sheet['C' + str(i)].value)
                if (coursePattern.match(courseID) and intakePattern.match(courseIntake)):
                    self.intakeDict[courseID] = courseIntake
                    
        
    #END of processIntakeInfo()
    
    def processCourseInfo(self, response):
        
        # Ngee Ann Poly Course
        if (response.url.lower().startswith("https://www1.np.edu.sg/")): 
            for courseObj in self.courseNPList:
                if (courseObj.url2 == response.url):
                    # Extract course description
                    courseObj.setDesciption(self.processStringList(response.xpath(".//article[@class='a2_art_1']//p//text()").extract()))
        if (response.url.lower().startswith("http://www.np.edu.sg/")): 
            for courseObj in self.courseNPList:
                if (courseObj.url == response.url):
                    # Extract course meta tag (HAS NO META DATA)
                    #courseObj.setMeta(self.processString(response.xpath("//meta[@name='keywords']/@content")[0].extract()))
                    # Extract course structure
                    structDict = {'1:Year 1': {}, '2:Year 2': {}, '3:Year 3': {}}
                    currentYear = '1:Year 1'
                    currentSem = 'Semester 1'
                    for mod in response.xpath("//div[@id='menutab_1_5']//table[1]//tr"):
                        if (len(mod.xpath(".//td[3]//text()").extract()) > 0 and len(self.processString(mod.xpath(".//td[3]//text()").extract()[0])) > 0):
                            modYear = self.processString(mod.xpath(".//td[3]//text()").extract()[0])
                            if (modYear.startswith("Level 1.1")):
                                currentYear = '1:Year 1'
                                currentSem = 'Semester 1'
                            elif (modYear.startswith("Level 1.2")):
                                currentYear = '1:Year 1'
                                currentSem = 'Semester 2'
                            elif (modYear.startswith("Level 2.1")):
                                currentYear = '2:Year 2'
                                currentSem = 'Semester 1'
                            elif (modYear.startswith("Level 2.2")):
                                currentYear = '2:Year 2'
                                currentSem = 'Semester 2'
                            elif (modYear.startswith("Level 3.1")):
                                currentYear = '3:Year 3'
                                currentSem = 'Semester 1'
                            elif (modYear.startswith("Level 3.2")):
                                currentYear = '3:Year 3'
                                currentSem = 'Semester 2'
                            structDict[currentYear][currentSem] = []
                        elif (len(mod.xpath(".//td[3]//span[@class='grdModuletext']//text()").extract()) > 0):
                            structDict[currentYear][currentSem].append(self.processString(mod.xpath(".//td[3]//span[@class='grdModuletext']//text()").extract()[0]))
                    courseObj.setStructure(json.dumps(structDict))
        
        # Republic Poly Course
        if (response.url.lower().startswith("http://www.rp.edu.sg/")): 
            for courseObj in self.courseRPList:
                if (courseObj.url == response.url):
                    # Extract course meta tag (HAS NO META DATA)
                    # courseObj.setMeta(self.processString(response.xpath("//meta[@name='keywords']/@content")[0].extract()))
                    # Extract course description
                    courseObj.setDesciption(self.processStringList(response.xpath(".//div[@class='coursetab']//table//table//tr[3]//text()").extract()))
                    # Extract course structure
                    structDict = {'1:General': {}, '2:Discipline': [], '3:Specialisation': {}}
                    structDict['1:General']['Modules'] = []
                    structDict['1:General']['Programs'] = []
                    i = 1 # Table Index
                    while True:
                        tableHeader = response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[1]//font/text()").extract()
                        if (not len(tableHeader) > 0):
                            break
                        else:
                            if (tableHeader[0].startswith("General")):
                                for mod in response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//a//text()"):
                                    if (len(self.processString(mod.extract())) > 1):
                                        structDict['1:General']['Modules'].append(self.processString(mod.extract()))
                            elif (tableHeader[0].startswith("Freely")):
                                structDict['1:General']['Modules'].append(self.processString(tableHeader[0]))
                            elif (tableHeader[0].startswith("Discipline")):
                                for mod in response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//a//text()"):
                                    if (len(self.processString(mod.extract())) > 1):
                                        structDict['2:Discipline'].append(self.processString(mod.extract()))
                            elif (tableHeader[0].startswith("Industry")):
                                for mod in response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//a//text()"):
                                    if (len(self.processString(mod.extract())) > 1):
                                        structDict['1:General']['Programs'].append(self.processString(mod.extract()))
                            elif (tableHeader[0].startswith("Specialisation")):
                                multi_elective = response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//p//text()").extract()
                                # Has multiple elective
                                if (len(multi_elective) > 0 and multi_elective[0].startswith("Choose")): 
                                    # Electives formatted by multiple TR (Horizontally)
                                    if (len(response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[3]//p//text()").extract()) > 0):
                                        electiveIndex = 1
                                        while True: # Loop thru all elective options
                                            electiveHeader = response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[3]//td[" + str(electiveIndex) + "]//strong//text()").extract()
                                            if (len(electiveHeader) > 0):
                                                structDict['3:Specialisation'][str(electiveHeader[0].strip())] = []
                                                for mod in response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[3]//td[" + str(electiveIndex) + "]//a//text()"):
                                                    if (len(self.processString(mod.extract())) > 1):
                                                        structDict['3:Specialisation'][electiveHeader[0].strip()].append(self.processString(mod.extract()))
                                                electiveIndex +=1
                                            else:
                                                break
                                    # Electives formatted by single TD (Vertically)
                                    elif (str(response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//strong//text()").extract()[0]).startswith("Option")) :
                                        track = ""
                                        for mod in response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//text()"):
                                            text =  self.processString(mod.extract())
                                            if (len(text) > 0 and not text.startswith("Choose")):
                                                if (text.startswith("Option")):
                                                    track = text[text.index(':')+2:]
                                                    structDict['3:Specialisation'][track] = []
                                                else:
                                                    structDict['3:Specialisation'][track].append(text)
                                                
                                # Doesnt have multiple electives
                                else:
                                    structDict['3:Specialisation']['Single Track'] = []
                                    for mod in response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//a//text()"):
                                        if (len(self.processString(mod.extract())) > 1):
                                            structDict['3:Specialisation']['Single Track'].append(self.processString(mod.extract()))
                            elif (tableHeader[0].startswith("Elective")):
                                structDict['3:Specialisation']['Elective (Select One)'] = []
                                for mod in response.xpath("//ul[@id='desc']//li[3]//textarea//table[" + str(i) + "]//tr[2]//a//text()"):
                                    if (len(self.processString(mod.extract()).strip()) > 1):
                                        structDict['3:Specialisation']['Elective (Select One)'].append(self.processString(mod.extract()))
                                        
                            i +=1
                    courseObj.setStructure(json.dumps(structDict))
                        
        # Singapore Poly Course
        if (response.url.lower().startswith("http://m.sp.edu.sg/")): 
            for courseObj in self.courseSPList:
                if (courseObj.url2 == response.url):
                    # Extract course description
                    courseObj.setDesciption(self.processStringList(response.xpath(".//div[@id='collapseOne']//p[1]//text()").extract()))
                    # Extract course meta tag
                    courseObj.setMeta(self.processString(response.xpath("//meta[@name='keywords']/@content")[0].extract()))
                    # Extract course structure
                    structDict = {'1:Year 1': [], '2:Year 2': [], '3:Year 3': [], '4:Advanced Modules (optional)' :[]}
                    for mod in response.xpath("//div[@id='collapseFive']//ul[1]//li//text()"):
                            structDict['1:Year 1'].append(mod.extract())
                    for mod in response.xpath("//div[@id='collapseFive']//ul[2]//li//text()"):
                            structDict['2:Year 2'].append(mod.extract())
                    for mod in response.xpath("//div[@id='collapseFive']//ul[3]//li//text()"):
                            structDict['3:Year 3'].append(mod.extract())
                    for mod in response.xpath("//div[@id='collapseFive']//ul[4]//li//text()"):
                            structDict['4:Advanced Modules (optional)'].append(mod.extract())
                    courseObj.setStructure(json.dumps(structDict))
                   
        # Nanyang Poly Course
        if (response.url.lower().startswith("http://www.nyp.edu.sg")): 
            for courseObj in self.courseNYPList:
                if (courseObj.url == response.url):
                    # Extract course description
                    for desc in response.xpath(".//div[@class='list-content col-lg-12']//div[@class='ds-richtext']//p//text()"):
                        descStr = self.processString(desc.extract())
                        if (len(descStr) > 0):
                            courseObj.description = courseObj.description + descStr + "\r\n"
                    # Extract course meta tag
                    courseObj.setMeta(self.processString(response.xpath("//meta[@name='keywords']/@content")[0].extract()))
                    # Extract course structure
                    structDict = {}
                    yearList = []
                    subCatList = [] 
                    for yearPanel in response.xpath("//h4[@class='panel-title']//text()"): # Collect all Year panel title
                        yearCat = self.processString(yearPanel.extract())
                        if (len(yearCat) > 0):
                            yearList.append(yearCat)
                    for mod in response.xpath("//div[@class='panel-body']//b//text()"): # Collect all sub category title
                        subCat = self.processString(mod.extract())
                        if (len(subCat) > 0 ):
                            subCatList.append(subCat)
                    year = 0
                    subYear = 0
                    if (len(subCatList) > 1):
                        for yearPanel in response.xpath("//div[@class='panel-body']"): # For each accordion tab
                            structDict[yearList[year]] = {}
                            for category in yearPanel.xpath(".//ul"): # For each list in accordion tab
                                try:
                                    structDict[yearList[year]][subCatList[subYear]] = []
                                except IndexError:
                                            print "Index Error: Out of Range"
                                            print response.url
                                if (response.url.lower().startswith("http://www.nyp.edu.sg/schools/sit/full-time-courses/information-technology.html")): # Special course with multi sub elective
                                    for mod in category.xpath(".//ul//li//text()"):
                                        if (len(self.processString(mod.extract())) > 0):
                                            structDict[yearList[year]][subCatList[subYear]].append(self.processString(mod.extract()))
                                else:
                                    for mod in category.xpath(".//li//text()"):
                                        if (len(self.processString(mod.extract())) > 0):
                                            structDict[yearList[year]][subCatList[subYear]].append(self.processString(mod.extract()))
                                    exception = self.processString(category.xpath(".//li//text()").extract()[0]) # Dont skip FYP or ITP option list
                                    if (not exception.startswith("Teaching") and not exception.startswith("Internship")):
                                        subYear +=1
                            year +=1
                    else:
                        # For special courses like: http://www.nyp.edu.sg/schools/seg/full-time-courses/aerospace-electrical-electronics-programme.html
                        for yearPanel in response.xpath("//div[@class='panel-body']"): # For each accordion tab
                            structDict[yearList[year]] = []
                            for mod in yearPanel.xpath(".//li//text()"):
                                if (len(self.processString(mod.extract(), True)) > 0):
                                    try:
                                        structDict[yearList[year]].append(self.processString(mod.extract()))
                                    except IndexError:
                                        print "Index Error: Out of Range"
                                        print response.url
                            year +=1
                    courseObj.setStructure(json.dumps(structDict))
                        
        # Temasek Poly Course
        if (response.url.lower().startswith("http://www.tp.edu.sg/")): 
            for courseObj in self.courseTPList:
                if (courseObj.url == response.url):
                    # Extract course meta tag
                    courseObj.setMeta(self.processString(response.xpath("//meta[@name='keywords']/@content")[0].extract()))
                    # Extract course description
                    courseObj.setDesciption(self.processStringList(response.xpath(".//div[@class='tab-content']//div[@id='tab1']//p/text()").extract()))
                    # Extract course structure
                    structDict = {'1:Year 1': [], '2:Year 2': [], '3:Year 3': [], '4:Electives':{}}
                    for mod in response.xpath("//div[@id='tab6']//table[1]//tbody[1]//tr"): # Extract from Core Subjects
                        mod_name =  mod.xpath(".//td//a//text()").extract()
                        mod_lv =  mod.xpath(".//td[3]//text()").extract()[0]
                        if (len(mod_name) > 0):
                            if (mod_lv == '1'):
                                structDict['1:Year 1'].append(self.processString(mod_name[0]))
                            elif (mod_lv == '2'):
                                structDict['2:Year 2'].append(self.processString(mod_name[0]))
                            elif (mod_lv == '3'):
                                structDict['3:Year 3'].append(self.processString(mod_name[0]))
                    for mod in response.xpath("//div[@id='tab6']//table[2]//tbody[1]//tr"): # Extract from Diploma Subjects
                        mod_name =  mod.xpath(".//td//a//text()").extract()
                        mod_lv =  mod.xpath(".//td[3]//text()").extract()[0]
                        if (len(mod_name) > 0):
                            if (mod_lv == '1'):
                                structDict['1:Year 1'].append(self.processString(mod_name[0]))
                            elif (mod_lv == '2'):
                                structDict['2:Year 2'].append(self.processString(mod_name[0]))
                            elif (mod_lv == '3'):
                                structDict['3:Year 3'].append(self.processString(mod_name[0]))
                        
                    # Elective modules handling
                    electiveHeader = self.processString(response.xpath("//div[@id='tab6']/h3[3]//text()").extract()[0], False)
                    if (electiveHeader.endswith("Elective Subjects") or response.url.lower().endswith("veterinary-technology-t45")): # Elective Subjects by list or entire table
                        # Make exception for veterinary tech, that website fcke dup not consistent one
                        listExist = response.xpath("//div[@id='tab6']/ul/li//text()").extract()
                        if (len(listExist) > 1):
                            i=3
                            for elective in response.xpath("//div[@id='tab6']/ul/li//text()"): # Extract from Diploma Subjects
                                structDict['4:Electives'][self.processString(elective.extract())] = []
                                for mod in response.xpath("//div[@id='tab6']//table[" + str(i) + "]//tbody[1]//tr//td//a//text()"): # Extract from Diploma Subjects
                                    structDict['4:Electives'][elective.extract()].append(self.processString(mod.extract()))
                                i+=1
                        else:
                            structDict['4:Electives'] = []
                            for elective in response.xpath("//div[@id='tab6']//table[3]//tbody[1]//tr"): # Extract mods from elective section
                                mod_name =  elective.xpath(".//td//a//text()").extract()     
                                if (len(mod_name) > 0):
                                    structDict['4:Electives'].append(self.processString(mod_name[0]))
                                
                    elif (electiveHeader.endswith("Elective Cluster Subjects") ): # Elective in cluster forms
                        i=3
                        for elective in response.xpath("//div[@id='tab6']/p//text()"): # Extract from Diploma Subjects
                            if (not elective.extract().startswith("Students") and not elective.extract().startswith("Cross") and len(elective.extract()) > 1):
                                structDict['4:Electives'][self.processString(elective.extract())] = []
                                for mod in response.xpath("//div[@id='tab6']//table[" + str(i) + "]//tbody[1]//tr//td//a//text()"): # Extract from Diploma Subjects
                                    structDict['4:Electives'][elective.extract()].append(self.processString(mod.extract()))
                            i+=1
                    courseObj.setStructure(json.dumps(structDict))
        
        
                        
    #END of processCourseInfo()
    
    def processString(self, string, strip = True):
        result = ""
        if (len(string) > 0):
            result = string.replace(u'\xa0', u' ') # Remove &nbsp
            result = result.replace(u'\r', '').replace(u'\n', '') # Remove breaklines
            result = re.sub( '\s+', ' ', result ) # Merge spaces
            result = result.replace(u'\u2013', '-') # Replace unicode dash lines
            result = result.replace('&amp', '&') # Replace unicode & characters
            if (strip):
                result = result.strip()
        return str(result.encode('ascii', 'ignore'))
    #END of processString()
    
    def processStringList(self, strList):
        result = ""
        for str in strList:
            str = self.processString(str)
            if (len(str) > 1):
                result = result + str
                if (str[-1] == '.'): # Make sure its really end of sentence for paragraphing
                    result = result + "\\r\\n"
        return result
    
    def closed(self, reason):
        self.driver.close()
        with open("./PolyData.pkl", "wb") as pickle_file:
            for courseObj in self.courseList:
                courseObj.setTimestamp(datetime.datetime.utcnow())
                if (courseObj.courseID in self.intakeDict):
                    courseObj.setIntake(self.intakeDict[courseObj.courseID])
                if (not len(courseObj.description) > 0):
                    courseObj.setDesciption("No information available")
                pickle.dump(courseObj, pickle_file, pickle.HIGHEST_PROTOCOL)

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SP_MobileSpider)
    yield runner.crawl(PolySpider)
    reactor.stop()

crawl()
reactor.run()