from google.appengine.ext import ndb

def insertCourse(course_id, poly, score, name, url, ext_info, course_type, year):
    entity = model_jae.create_entity(course_id, poly, score, name, url, ext_info, course_type, year)
    return entity.put()

def delCourse(course_id):
    key = model_jae.get_key(course_id)
    return key.delete()

def get_course_by_id(course_id):
    # getting only 1 course
    return model_jae.get_key(course_id).get();

def get_course_list(size=10, nOffset=0, *ordering):
    '''returns a list object'''
    #ordering is only able to take in multiple or no ndb.model.properties
    qry = model_jae.query()
    
    # added to support model_jae.get_properties_from_str()
    if(len(ordering) is not 0 and type(ordering[0]) is list):
        ordering = ordering[0]
    
    for order in ordering:
        qry = qry.order(order)
        
    return qry.fetch(size, offset=nOffset)

class bulkDeleter:
    # builder to simplify adding of entities
    def __init__(self):
        self.list_keys = []
     
    def add_key(self, course_id):
        key = model_jae.get_key(course_id)
        
        self.list_keys.append(key)
        
        #returns self for method chaining
        return self
 
    def size(self):
        return len(self.list_keys)
     
    def remove_from_database(self):
        #returns a list keys from the entities
        return ndb.delete_multi(self.list_keys)
    
    def refresh(self):
        #clears the list such that builder can be 'reused'
        del self.list_entity[:]

class entityListBuilder:
    # builder to simplify adding of entities
    def __init__(self):
        self.list_entity = []
     
    def add_entity(self, course_id, poly, score, name, url, ext_info, course_type, year):
        entity = model_jae.create_entity(course_id, poly, score, name, url, ext_info, course_type, year)
        
        self.list_entity.append(entity)
        
        #returns self for method chaining
        return self
 
    def size(self):
        return len(self.list_entity)
     
    def add_to_database(self):
        #returns a list keys from the entities
        return ndb.put_multi(self.list_entity)
    
    def refresh(self):
        #clears the list such that builder can be 'reused'
        del self.list_entity[:]
        
class model_jae(ndb.Model):    
    poly = ndb.StringProperty() # Polytechnic Acronym
    id = ndb.StringProperty() # Course ID
    score = ndb.StringProperty() # O' level Score Requirement
    name = ndb.StringProperty() # Course Name
    url = ndb.TextProperty() # Course URL Info
    ext_info = ndb.StringProperty() # Additional info
    course_type = ndb.StringProperty()  # course_type = applied sciences, etc
    year = ndb.StringProperty() # The year this entry is collected
    
    '''method to easily create an entity'''
    @staticmethod
    def create_entity(course_id, poly, score, name, url, ext_info, course_type, year):
        entity = model_jae()
        entity.poly = poly;
        entity.score = score;
        entity.name = name;
        entity.url = url;
        entity.course_type = course_type;
        entity.year = year;
     
        entity.id = course_id;
        entity.key = model_jae.get_key(course_id)
        return entity
    
    @staticmethod
    def get_key(course_id):
        return ndb.Key(model_jae, course_id)
    
    @staticmethod
    def get_properties_from_str(*properties):       
        _properties = []

        for prop in properties:
            if prop[0] is '-':
                _properties.append(model_jae._properties[prop[1:]])
            else:
                _properties.append(model_jae._properties[prop])
            
        return _properties
    