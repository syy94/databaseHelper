from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')  # URL '/' to be handled by main() route handler

def main():
    return render_template('index.html')
 
@app.route('/serviceList')
def serviceList():
    # refresh database code moved to cron/update data.py
    # to change the date that cron runs, see cron.yaml 
    return render_template('serviceList.html')
    
 
@app.errorhandler(500)
def server_error(e):
    return str(e)
 
if __name__ == '__main__':  # Script executed directly?
    app.run()  # Launch built-in web server and run this Flask webapp
    
