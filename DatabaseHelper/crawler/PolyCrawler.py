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

from itertools import islice
from DataType.iPolyCourse import iPolyCourse
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

        
'''
Initial Crawler to extract SP's course data from mobile version
'''
class SP_MobileSpider(scrapy.Spider):
    name = "SP_MobileSpider"
    
    def start_requests(self):
        urls = ['http://m.sp.edu.sg/courses']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        coursePattern = re.compile("^([A-Z]{1}[0-9]{2})$")  # Match Alphabet + 2 Digits
        with open("./SPMobile.csv", "wb") as csv_file:
            Results = response.xpath('//a[@class="courses-box-1"]/@href').extract()
            for rows in Results:
                courseID = "S" + rows[-2:]
                if (coursePattern.match(courseID)):
                    csv_file.write(courseID + "," + "http://m.sp.edu.sg/" + rows + "\r\n")
                    
class PolySpider(scrapy.Spider):
    name = "PolyIntake"
    intakeDict = {}
    courseList = [] # Contains list of all courses, be populated at the end by merging the ones below
    courseNPList = [] # List of NP course to be populated
    courseSPList = [] # List of SP course to be populated
    courseRPList = [] # List of RP course to be populated
    courseNYPList = [] # List of NYP course to be populated
    courseTPList = [] # List of TP course to be populated
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
    
    # Read custom CSV file containing SP's mobile url and store into Dict
    
    with open('SPMobile.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            spCourseURL[str(row[0])] = str(row[1])
        
    # Read all info from polytechnic.edu.sg's CSV file and populate whatever we can into courseList objects first.
    url_AllCourse = 'http://www.polytechnic.edu.sg/api/download/course?id=b434281c-efe6-69f6-9162-ff000003a8ed'
    cr = csv.reader(urllib2.urlopen(url_AllCourse))
    for row in islice(cr, 1, None): # Skip first item
        url = row[7]
        if (url[0] == "#"): # Some records have trailing # character, dont know why
            url = url[1:]
        if (url[-1] == "#"):
            url = url[:-1]
        courseObj = iPolyCourse(row[2], row[1], row[5], row[3], url, row[6])
        courseList.append(courseObj)
        if (url.startswith("http://www.np.edu.sg")):
            courseNPList.append(courseObj)
            url = url.lower()
            # Create mobile version of URL
            mobile_Ext = url[url.find("courses")+8:url.find("/pages")]
            if (mobile_Ext.find("fulltime") != -1):
                mobile_Ext = mobile_Ext[len("fulltime/"):]
            if (mobile_Ext.find("diploma") != -1):
                mobile_Ext = url[url.find("pages")+6:-5]
            
            mobile_Ext = "https://www1.np.edu.sg/EAE/CoursesAtAGlance/Courses/" + mobile_Ext + "/"
            courseObj.url2 = mobile_Ext
                
            courseURL.append(mobile_Ext)
            #courseURL.append(url)
        elif (url.startswith("http://www.nyp.edu.sg")):
            courseNYPList.append(courseObj)
            #courseURL.append(url)
        elif (url.startswith("http://www.tp.edu.sg")):
            courseTPList.append(courseObj)
            #courseURL.append(url)
        elif (url.startswith("http://www.rp.edu.sg")):
            courseRPList.append(courseObj)   
            #courseURL.append(url)
        elif (url.startswith("http://www.sp.edu.sg")):
            try:
                #courseURL.append(spCourseURL[row[2]])
                courseObj.setURL2(spCourseURL[row[2]])
                courseSPList.append(courseObj)
            except KeyError:
                print "Course ID: " + row[2] + " not found!"
            
    def start_requests(self):
        urls = []
        urls.extend(self.intakeURL)
        urls.extend(self.courseURL)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    #END of start_requests()

    def parse(self, response):
        
        if response.url in self.intakeURL:
            self.processIntakeInto(response)
        else:
            self.processCourseInfo(response)              
            #pprint.pprint(self.intakeDict)        
    #END of parse()
    
    def processIntakeInto(self, response):
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
                    courseObj.setDesciption(self.processStringList(response.xpath(".//article[@class='a2_art_1']//p//text()").extract()))
                    print self.processStringList(response.xpath(".//article[@class='a2_art_1']//p//text()").extract())
                    '''
                    if (response.url.lower().startswith("http://www.np.edu.sg/de")): # School of Design
                        courseObj.setDesciption(self.processStringList(response.xpath(".//div[@id='menutab_1_1']//tbody//tr[3]//text()").extract()))
                    elif (response.url.lower().startswith("http://www.np.edu.sg/lsct")): # School of Design
                    '''
        
        # Republic Poly Course
        if (response.url.lower().startswith("http://www.rp.edu.sg/")): 
            for courseObj in self.courseRPList:
                if (courseObj.url == response.url):
                        courseObj.setDesciption(self.processStringList(response.xpath(".//div[@class='coursetab']//table//table//tr[3]//text()").extract()))
                        
        # Singapore Poly Course
        if (response.url.lower().startswith("http://m.sp.edu.sg/")): 
            for courseObj in self.courseSPList:
                if (courseObj.url == response.url):
                    courseObj.setDesciption(self.processStringList(response.xpath(".//div[@id='collapseOne']//p[1]//text()").extract()))
                   
        # Nanyang Poly Course
        if (response.url.lower().startswith("http://www.nyp.edu.sg/")): 
            for courseObj in self.courseNYPList:
                if (courseObj.url == response.url):
                        courseObj.setDesciption(self.processStringList(response.xpath(".//section[@class='school-course-about ds-component-margin']//div[@class='ds-richtext']//p//text()").extract()))
        
        # Temasek Poly Course
        if (response.url.lower().startswith("http://www.tp.edu.sg/")): 
            for courseObj in self.courseTPList:
                if (courseObj.url == response.url):
                        courseObj.setDesciption(self.processStringList(response.xpath(".//div[@class='tab-content']//div[@id='tab1']//p/text()").extract()))
            
    #END of processCourseInfo()
    
    def processString(self, string):
        result = string.replace(u'\xa0', u' ') # Remove &nbsp
        result = result.replace(u'\r', '').replace(u'\n', '') # Remove breaklines
        result = re.sub( '\s+', ' ', result ) # Merge spaces
        result = result.replace(u'\u2013', '-') # Replace funny dash lines
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

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SP_MobileSpider)
    yield runner.crawl(PolySpider)
    reactor.stop()

crawl()
reactor.run()