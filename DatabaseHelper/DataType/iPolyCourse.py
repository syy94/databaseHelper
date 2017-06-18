'''
Created on May 20, 2017

@author: Choony

Initial Note - To be removed
All objects be stored in DataType folder, naming sequences will all begin with 'i' to indicate instance objects
It is likely that we will expand to Diploma - Plus Courses, part time courses, ITE/Uni courses and so on. 
Hence, all data types will be stored here for naming & field type consistency, while backend can be written seperately.
Rmbr to include object type checking for writing/deleting of entries to datastore, likely will expand another datastore to store 
different types of objects. So all poly full time courses will have its own datastore and so on
'''

class iPolyCourse:
    
    courseID = ""       # Course ID             (E.g. T51)
    polytechnic = ""    # Polytechnic Acronym   (E.g. NP)
    score = 0           # O' Level Score        (E.g. 12)
    name  = ""          # Course name           (E.g. Diploma In ABC)
    url = ""            # Course URL            (Direct link to school site)
    url2 = ""           # Secondary URL         (Second Course URL)
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
    
    Course price and duration are standardized throughout the poly, hence likely to write seperate function to check if looking 
    for wat type of education and which poly, then return value so that can reduce DB redundancy
    '''
    
    
    def __init__(self, courseID, polytechnic="", score=0, name="", url="", year=0):
        self.courseID = courseID # Course ID is mandatory
        self.polytechnic = polytechnic
        self.score = score
        self.name = name
        self.url = url
        self.year = year
        
    def setDesciption(self, description): 
        self.description = description
        
    def setProspect(self, prospect):
        self.prospect = prospect
        
    def setURL2(self, url2):
        self.url2 = url2
        
    def setEmployment(self, employment):
        self.employment = employment # Likely to be serialized into JSON data
    