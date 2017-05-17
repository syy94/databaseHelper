import database

from string import ascii_lowercase
from flask import Flask, render_template
from database import entityListBuilder

app = Flask(__name__)

@app.route('/')  # URL '/' to be handled by main() route handler
def main():
    
    # logging.info(str(database.get_course_list(3, 0)) + '<br><br>' + str(database.get_course_list(3, 0, -model_jae.poly, -model_jae.course_type)))
    return str(database.get_course_by_id('a'))
    
    return render_template('index.html') 
 
@app.route('/serviceList')
def serviceList():

    builder = entityListBuilder()
    
    for c in ascii_lowercase:
        builder.add_entity(c, c + 'BP2', c + 'S', c + 'bird', c + 'street', 'info?', c + 'childhood')
      
    builder.add_to_database()
    
    return 'refreshed database'
    

@app.errorhandler(500)
def server_error(e):
    return str(e)
 
if __name__ == '__main__':  # Script executed directly?
    app.run()  # Launch built-in web server and run this Flask webapp
