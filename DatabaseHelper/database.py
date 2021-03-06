from google.appengine.api import search
from google.appengine.ext import ndb
import logging

def insertCourse(course_id, poly, score, name, url, description, course_type, year, structure):
    entity = model_jae.create_entity(course_id, poly, score, name, url, description, course_type, year, structure)
    return entity.put()

def delCourse(course_id):
    key = model_jae.get_key(course_id)
    return key.delete()

def get_course_by_id(course_id):
    # getting only 1 course
    return model_jae.get_key(course_id).get();

def get_favs(id_list):
    key_list = [(model_jae.get_key(myId)) for myId in id_list]
    
    return [{
            "name": course.name,
            "poly": course.poly,
            "score": course.score,
            "id": course.id
        } for course in ndb.get_multi(key_list)]

def get_course_list(jsonInput):
    '''
    takes in Jsonobject containing:
    
    size: int (optional, default value 20)
    offset: int (optional, default value 0)
    orders: [str] (optional)
    
    returns a list object
    '''
    
    # ordering is only able to take in multiple or no ndb.model.properties
    try:
        qry = model_jae.query(model_jae.poly == str(jsonInput["school"]))
    except:
        qry = model_jae.query()
    # projection = [model_jae.name, model_jae.poly, model_jae.score, model_jae.id]
    
    ordering = model_jae.get_properties_from_str(jsonInput['orders'])
    # added to support model_jae.get_properties_from_str()
    if(len(ordering) is not 0 and type(ordering[0]) is list):
        ordering = ordering[0]
     
    for order in ordering:
        qry = qry.order(order)
        
    keys = qry.fetch(jsonInput['size'], offset=jsonInput['offset'], keys_only=True)
    
    # added the extra processing to return name, poly and score and id to minimize size of 
    # data sent through the web.
    
    result = []
    
    for course in ndb.get_multi(keys):
        result.append({
            "name": course.name,
            "poly": course.poly,
            "score": course.score,
            "id": course.id
        })
    
    return result;

def find(queryStr, offset):
    query_options = search.QueryOptions(
        limit=40,
        offset=offset,
        returned_fields=['id', 'name', 'score', 'poly'])
    
    query = search.Query(query_string=''.join(['terms:', queryStr]), options=query_options)
    
    q_result = model_jae.get_search_Index().search(query)

    result = [];
    
    for doc in q_result.results:
        course = {};
        
        for field in doc.fields:
            course[field.name] = field.value
        
        result.append(course)
        
    return result;

class bulkDeleter:
    # builder to simplify adding of entities
    def __init__(self):
        self.list_keys = []
     
    def add_key(self, course_id):
        key = model_jae.get_key(course_id)
        
        self.list_keys.append(key)
        
        # returns self for method chaining
        return self
 
    def size(self):
        return len(self.list_keys)
     
    def remove_from_database(self):
        # returns a list keys from the entities
        return ndb.delete_multi(self.list_keys)
    
    def refresh(self):
        # clears the list such that builder can be 'reused'
        del self.list_entity[:]

class entityListBuilder:
    # builder to simplify adding of entities
    def __init__(self):
        self.list_entity = []
     
    def add_entity(self, course_id, poly, score, name, url, url2, description, year, structure, cluster, intake):
        entity = model_jae.create_entity(course_id, poly, int(score), name, url, url2, description, year, structure, cluster, str(intake))
        
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
    score = ndb.IntegerProperty() # O' level Score Requirement
    name = ndb.StringProperty() # Course Name
    url = ndb.TextProperty() # Course URL Info
    url2 = ndb.TextProperty() # Second URL
    intake = ndb.StringProperty()
    cluster = ndb.StringProperty()
    description = ndb.TextProperty() # Course Description
    year = ndb.StringProperty() # The year this entry is collected
    structure = ndb.TextProperty() # Course structure (JSON)
    
    @staticmethod
    def get_search_Index():
        return search.Index('search')
    
    def _post_put_hook(self, future):
        # super
        ndb.Model._post_put_hook(self, future)
        # Post hooks do not check whether the RPC was successful; the hook runs regardless of failure.
        doc = search.Document(
            doc_id=self.id,
            fields=[
                search.TextField(name='terms', value=self.get_search_terms()),
                search.TextField(name='id', value=self.id),
                search.TextField(name='name', value=self.name),
                search.NumberField(name='score', value=int(self.score)),
                search.TextField(name='poly', value=self.poly)
            ]);
            
        search.Index('search').put(doc)
    
    def get_search_terms(self):
        terms = []
        terms.append(self.id)
        terms.append(self.poly)
        terms.append(str(self.score))
        
        for word in str(self.name).split():
            cursor = 1
            while True:
                # this method produces pieces of 'TEXT' as 'TEX,TEXT'
                terms.append(word[:cursor])
            
                # optionally, you can do the following instead to procude
                # 'TEXT' as 'T,E,X,T,TE,EX,XT,TEX,EXT,TEXT'
                #
                # for i in range(len(word) - cursor + 1):
                #    pieces.append(word[i:i + cursor])
            
                if cursor == len(word): break
                cursor += 1
        
        return ','.join(terms);
    
    @classmethod
    def _post_delete_hook(cls, key, future):
        super(model_jae, cls)._post_delete_hook(key, future)
        
        search.Index('search').delete(key.id())
    
    '''method to easily create an entity'''
    @staticmethod
    def create_entity(course_id, poly, score, name, url, url2, description, year, structure, cluster, intake):
        entity = model_jae()
        entity.id = course_id;
        entity.poly = poly;
        entity.score = score;
        entity.name = name;
        entity.url = url;
        entity.url2 = url2
        entity.description = description
        entity.year = year;
        entity.structure = structure
        entity.cluster = cluster
        entity.intake = intake
     
        entity.key = model_jae.get_key(course_id)
        return entity
    
    @staticmethod
    def get_key(course_id):
        return ndb.Key(model_jae, course_id)
    
    @staticmethod
    def get_properties_from_str(properties):
        _properties = []

        # if first char is '-', means that it should be in descending order
        for prop in properties:
            if str(prop)[0] is '-':
                _properties.append(-model_jae._properties[str(prop)[1:]])
            else:
                _properties.append(model_jae._properties[prop])
            
        return _properties
    