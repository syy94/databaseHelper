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

class iITECourse(object):
    
    name  = ""          # Course name           (E.g. Higher Nitec in Accounting)
    requirement = ""    # Grade requirements    (In JSON Listing)
    url = ""            # Course URL            (Direct link to school site)
    structure = ""      # Course Structure      (Structure stored in JSON format
    ext_info = ""       # Extra Info            (Course specific only)
    description = ""    # Course Description    (Paragraph on course description - URL Crawling)
    prospect = ""       # Career Prospect       (Paragraph on Career Prospect - URL Crawling)
    employment = ""     # Employment Data       (Data gathered regarding employment - DEEP Web Crawling) 
    metatag = ""        # Meta data             (Keywords extracted from meta tags)
    timestamp = 0       # Unix Timestamp        (Timestamp for data extraction date)
    
    '''
    Note: ext_info & employment will be leaved blank for now will further plans, take them as reserved space. 
    Description and Prospect will likely be lenght text, will suggest putting them tgt as a page in a tab, 
    while the rest of the data be in a single page. Likely 3rd page will be employment details
    
    Course price and duration are standardized throughout the poly, hence likely to write seperate function to check if looking 
    for wat type of education and which poly, then return value so that can reduce DB redundancy
    '''
    
    
    def __init__(self, courseID, polytechnic="", score=0, name="", url="", year=0, cluster=""):
        self.courseID = courseID # Course ID is mandatory
        self.polytechnic = polytechnic
        self.score = score
        self.name = name
        self.url = url
        self.year = year
        self.cluster = cluster
        
    def __repr__(self):
        return self
        
    def setDesciption(self, description): 
        self.description = description
        
    def setProspect(self, prospect):
        self.prospect = prospect
        
    def setStructure(self, structure):
        self.structure = structure
        
    def setMeta(self, meta):
        self.metatag = meta
        
    def setTimestamp(self, time):
        self.timestamp = time
        
    def setEmployment(self, employment):
        self.employment = employment # Likely to be serialized into JSON data
    