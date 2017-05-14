from google.appengine.ext import vendor
import os
import sys

# Add any libraries install in the "lib" folder.
vendor.add('libs')

"""https://github.com/gae-init/gae-init/pull/527
    fix for some msvcrt problem check link to find out more
"""
if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    sys.path.insert(0, 'lib.zip')
else:
    if os.name == 'nt':
        os.name = None
        sys.platform = ''