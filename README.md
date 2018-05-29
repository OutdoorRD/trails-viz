# trails-viz

Prototyping a web-app to display model predictions of trail use.

## Development

The flask application is contained within the "trails_site" directory. To develop with this application, you should set up a virtual environment outside of the repository. Activate this virtual environment, then navigate to the "trails_site" folder in the repository. Install the requirements by using the command ```pip install --editable .``` . This should install all requirements in your virtual environment to locally develop the flask application.

To run the application, activate your virtual environment and navigate to the trails_site/trails_site folder. Execute the following command: ```export FLASK_APP=trails_site```

Then, while in the same directory, execute the following command:  ```flask run```

The flask app should now be running on localhost:5000.
You can terminate the flask app by pressing 'control + c' in the terminal.

Note that when a change is made to the files, the app should be terminated and you should re-execute ```flask run```
