'''
Created on May 14, 2017

@author: Choony
'''
import scrapy
import csv
import urllib2
import DataType
import pprint
import re

from scrapy.crawler import CrawlerProcess

class PolySpider(scrapy.Spider):
    name = "PolyIntake"
    dictIntake = {}
    
    # List of URLs here
    url_RP = 'http://www.rp.edu.sg/Admissions_Information/Admissions/Planned_Intake_Figures.aspx'
    url_SP = 'http://www.sp.edu.sg/wps/portal/vp-spws/spws.fsu.courseintakesandcut-offpoints'
    url_TP = 'http://www.tp.edu.sg/admissions/course-intake-and-last-aggregate-scores'
    url_NP = 'http://www.np.edu.sg/admissions/before-apply/Pages/courses.aspx'
    xls_NYP = 'http://www.nyp.edu.sg/content/dam/nyp/admissions/full-time-diploma/admission-exercise/intake-and-jae-elr2b2-points/2017-intake-and-2016-elr2b2.xlsx'
    
    def start_requests(self):
        urls = [
            self.url_RP,
            self.url_SP,
            self.url_TP,
            self.url_NP
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        '''
        # Republic Poly URL Crawler
        if (response.url == self.url_RP):
            RPResults = response.xpath("//div[@class='content']//tr//td[not(contains(@bgcolor, '#6fb01e')) and contains(@align, 'center')]//text()").extract()
            i = 0
            while i < len(RPResults): # Returns a 1D-Arry of Course ID + Intake Size, parse 2 by 2
                self.dictIntake[RPResults[i].strip()] = RPResults[i+1].strip()
                i+=2
            
            
        # Singapore Poly URL Crawler
        if (response.url == self.url_SP):
            SPResults = response.xpath("//table[@id='tableDetails']//tr[not(contains(@class, 'yellow'))]//td//text()").extract()
            i = 0
            while i < len(SPResults): # Returns a 1D-Arry of Course Name (ID) + Intake Size + Score, parse 3 by 3
                courseID = SPResults[i]
                self.dictIntake[courseID[courseID.find("(")+len("("):courseID.rfind(")")].strip()] = SPResults[i+1].strip()
                i+=3
           
        # Temasek Poly URL Crawler
        if (response.url == self.url_TP):
            TPResults = response.xpath(".//table[@class='table table-bordered']//tbody")
            for rows in TPResults.xpath(".//tr[not(contains(@class, 'info bold'))]"):
                courseID = rows.xpath(".//td[(contains(@class, 'subheaderleft'))]//text()").extract()[0].strip() 
                courseIntake = rows.xpath(".//td[(contains(@class, 'intakeno'))]//text()").extract()[0].strip()
                self.dictIntake[courseID] = courseIntake
        '''
        # Ngee Ann Poly URL Crawler
        if (response.url == self.url_NP):
            NPResults = response.xpath(".//div[@class='ContentLeftHolder']//table[@border='1']")
            
            for rows in NPResults.xpath(".//tr[not(contains(@style, 'height:30pt'))]"):
                # NP tables got some entries that have weird char &#38203 taking up the first array or appending into the Course ID, so we always take last array (-1) and substring from char N
                courseID = rows.xpath(".//td[(contains(@width, '120'))]//text()").extract()[-1].encode('utf-8').strip()

                # Course Intake value will also have funny character, check if its digit, else index out for substring
                courseIntake = rows.xpath(".//td[(contains(@class, 'endcell'))]//text()").extract()[0].strip()
                i = 0;
                for c in courseIntake: 
                    if (c.isdigit() == False):
                        i+=1
                self.dictIntake[courseID[courseID.find("N"):]] = courseIntake[i:]

            
            pprint.pprint(self.dictIntake)
        # Nanyang Poly Intake Crawler
        # CSV File: http://www.nyp.edu.sg/content/dam/nyp/admissions/full-time-diploma/admission-exercise/intake-and-jae-elr2b2-points/2017-intake-and-2016-elr2b2.xlsx        

'''
url = 'http://www.polytechnic.edu.sg/api/download/course?id=b434281c-efe6-69f6-9162-ff000003a8ed'
response = urllib2.urlopen(url)
cr = csv.reader(response)

for row in cr:
    print row
'''
    
        
process = CrawlerProcess()
process.crawl(PolySpider)
process.start() # the script will block here until the crawling is finished