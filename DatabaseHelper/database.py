from google.appengine.ext import ndb

def insertCourse(course_id, poly, aggr_type, name, award, ext_info, course_type):
    entity = model_jae.create_entity(course_id, poly, aggr_type, name, award, ext_info, course_type)
    return entity.put()

def get_course_by_id(course_id):
    # getting only 1 course
    return model_jae.get_key(course_id).get();

def get_course_list(size, nOffset, *ordering):
    #ordering is only able to take in multiple or no ndb.model.properties
    qry = model_jae.query()
    
    # added to support model_jae.get_properties_from_str()
    if(len(ordering) is not 0 and type(ordering[0]) is list):
        ordering = ordering[0]
    
    for order in ordering:
        qry = qry.order(order)
        
    return qry.fetch(size, offset=nOffset)

class entityListBuilder:
    # builder to simplify adding of entities
    def __init__(self):
        self.list_entity = []
     
    def add_entity(self, course_id, poly, aggr_type, name, award, ext_info, course_type):
        entity = model_jae.create_entity(course_id, poly, aggr_type, name, award, ext_info, course_type)
        
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
    poly = ndb.StringProperty() # StringProperty is indexed (increases write ops)
    id = ndb.StringProperty()
    aggr_type = ndb.StringProperty()
    name = ndb.StringProperty()
    award = ndb.TextProperty() # TextProperty is not indexed (unable to be filtered by query)
    ext_info = ndb.StringProperty()
    course_type = ndb.StringProperty()  # course_type = applied sciences, etc
    
    '''method to easily create an entity'''
    @staticmethod
    def create_entity(course_id, poly, aggr_type, name, award, ext_info, course_type):
        entity = model_jae()
        entity.poly = poly;
        entity.aggr_type = aggr_type;
        entity.name = name;
        entity.award = award;
        entity.course_type = course_type;
     
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
                _properties.append(_dict[prop[1:]])
            else:
                _properties.append(_dict[prop])
            
        return _properties
    
_dict = {
    'poly' : model_jae.poly,
    'id' : model_jae.id,
    'aggr_type' : model_jae.aggr_type,
    'name' : model_jae.name,
    'award' : model_jae.award,
    'ext_info' : model_jae.ext_info,
    'course_type' : model_jae.course_type
}