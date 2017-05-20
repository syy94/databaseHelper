'''
Created on May 20, 2017

@author: Choony
'''

class iPolyCourse:
    
    courseID = ""       # Course ID             (E.g. T51)
    polytechnic = ""    # Polytechnic Acronym   (E.g. NP)
    score = 0           # O' Level Score        (E.g. 12)
    name  = ""          # Course name           (E.g. Diploma In ABC)
    url = ""            # Course URL            (Direct link to school site)
    year = 0            # Year timestamp        (Data is only relevant to specific year)
    intake = 0          # Course Intake         (E.g. 75, requires seperate URL + Data.gov Crawling)
    ext_info = ""       # Extra Info            (Course specific only)
    description = ""    # Course Description    (Paragraph on course description - URL Crawling)
    prospect = ""       # Career Prospect       (Paragraph on Career Prospect - URL Crawling)
    employment = ""     # Employment Data       (Data gathered regarding employment - DEEP Web Crawling) 
    
    '''
    Note: ext_info & employment will be leaved blank for now will further plans, take them as reserved space. 
    Description and Prospect will likely be lenght text, will suggest putting them tgt as a page in a tab, 
    while the rest of the data be in a single page. Likely 3rd page will be employment details
    '''
    
    def __init__(self, courseID):
        