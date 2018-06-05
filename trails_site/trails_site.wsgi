#import sys
#project_home = u'/var/www/html/trails-viz/trails_site'
#if project_home not in sys.path:
#    sys.path = [project_home] + sys.path
#activate_this = '/var/www/html/trails-viz/trails_site_venv/bin/activate_this.py'
#execfile(activate_this, dict(__file__=activate_this))

from trails_site import app as application
