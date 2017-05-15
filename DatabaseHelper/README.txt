App sturcture loosely follows the structure as listed here

https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env#basic_structure_of_an_app_project

	app.yaml: Configure the settings of the App Engine application
		#for handlers, whichever url satisfies the request will be 'activated'
			AKA ordering matters
			
	crawler: Directory to Store all the web crawlers.py
	
	cron: Directory to store the cron jobs
	
	libs: Directory to store all the third party libraries
		#referenced by appengine_config.py
		#see requirements.txt for installing new  libraries
	
	img: Directory to store the images
		#consider creating sub-directories if too many images
	
	main.py: Write the content of your application (Main page)
	
	requirements.txt: for pip to install the needed python libraries easily
		#pip install -t libs -r requirements.txt (install to /libs folder)
		#python -m pip install -r requirements.txt (install to your environment)
		#this file can be created by 'pip freeze' 
	
	static: Directory to store your static files (like css, etc)
	
	templates: Directory for all of your HTML templates
		#consider creating sub-directories if too many html files
		
Extras:
Consider following app structure as listed here:
	http://exploreflask.com/en/latest/organizing.html