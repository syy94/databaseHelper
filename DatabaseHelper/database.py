from google.appengine.ext import ndb

def insertCourse(course_id, poly, aggr_type, name, award, ext_info, course_type):
    entity = model_jae()
    entity.poly = poly;
    entity.aggr_type = aggr_type;
    entity.name = name;
    entity.award = award;
    entity.course_type = course_type;
    entity.key = ndb.Key(model_jae, course_id)
    
    entity.put()

class model_jae(ndb.Model):
    poly = ndb.StringProperty()
    aggr_type = ndb.StringProperty()
    name = ndb.StringProperty()
    award = ndb.StringProperty()
    ext_info = ndb.StringProperty()
    course_type = ndb.StringProperty() # applied sciences, etc