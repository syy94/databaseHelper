from database import entityListBuilder 
import pickle
from logging import info


PolyList = []
    
try:
    with open("./crawler/PolyData.pkl", 'rb') as polyFile:
        while True:  # loop indefinitely
            PolyList.append(pickle.load(polyFile))  # add each item from the file to a list
except EOFError:  
    info('EOF reached closing file to prevent mem leak')
    polyFile.close()
    pass
    
builder = entityListBuilder()
for courseObj in PolyList:
    builder.add_entity(
        courseObj.courseID
        , courseObj.polytechnic
        , courseObj.score
        , courseObj.name
        , courseObj.url 
        , courseObj.url2 
        , courseObj.description
        , courseObj.year
        , courseObj.structure
        , courseObj.cluster
        , courseObj.intake
    )
builder.add_to_database()
