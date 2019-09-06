# trails-viz

Prototyping a web-app to display model predictions of trail use.

## Developing

The flask application is contained within the "trails_site" directory. To develop with this application, you should set up a virtual environment outside of the repository. Activate this virtual environment, then navigate to the "trails_site" folder in the repository. Install the requirements by using the command ```pip install --editable .``` . This should install all requirements in your virtual environment to locally develop the flask application.

To run the application, activate your virtual environment and navigate to the trails_site/trails_site folder. Execute the following command: ```export FLASK_APP=trails_site```

Then, while in the same directory, execute the following command:  ```flask run```

The flask app should now be running on localhost:5000.
You can terminate the flask app by pressing 'control + c' in the terminal.

Note that when a change is made to the files, the app should be terminated and you should re-execute ```flask run```


## Deploying on apache
```
git clone https://github.com/davemfish/trails-viz
git checkout develop
```
copy mapbox-token.js to trails_site/trails_site/static/js

### setup a python virtual environment:
```virtualenv trails_site_env``` # python2 by default, which is fine

```source trails_site_env/bin/activate```

```pip install --editable .``` # from dir with setup.py

```deactivate```

### configure apache:
uncomment lines in trails_site.wsgi file

add these lines to virtualhosts.conf
```
<VirtualHost *:80>

    WSGIDaemonProcess trails_site user=apache group=apache threads=5
    ## below: a path in the webroot to redirect to the app's wsgi file.  no trailing slash!!!!
    WSGIScriptAlias /trails_site /var/www/html/trails-viz/trails_site/trails_site.wsgi

    <Directory /var/www/html/trails-viz/trails_site>
        WSGIProcessGroup trails_site
        WSGIApplicationGroup %{GLOBAL}
	Require all granted
    </Directory>

</VirtualHost>
```
restart apache
