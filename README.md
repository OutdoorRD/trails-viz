# Trails Visualization

A web-app to display model predictions of trail use.

[Build Status](https://app.travis-ci.com/github/OutdoorRD/trails-viz/builds?serverType=git)

## Development 

The project is split into two separate apps for front end and back end:
```bash
trails-viz/
  |- trails-viz-app
  |- trails-viz-api
```
`trails-viz-app` is the front end written in JavaScript using the [Vue](https://vuejs.org/) framework.
`trails-viz-api` is the backend written in Python using [Flask](https://palletsprojects.com/p/flask/)

Development requires nodejs >= 10.x.x and Python == 3.7.x

While opening the project in IDE, it's recommended to open the front end and backend as two separate projects. That way
the IDE would be able to recognize the former as a JavaScript project and the later as a Python project.

### Backend Setup
Install the dependencies globally or inside a [virtual environment](https://docs.python-guide.org/dev/virtualenvs/) 
(recommended). Navigate to the root of `trails-viz-api`, setup flask environment variables and start the 
development server. One app specific environment variable `DATA_FILES_ROOT` is required to set the location where
all the csv and shp files are:

```shell script
$ cd trails-viz-api
$ pip install -r requirements.txt
$ export FLASK_APP=trailsvizapi
$ export FLASK_ENV=development
$ export DATA_FILES_ROOT=<path/to/trails-viz-data/>
$ flask run
```
This will start a localhost server on port `5000`

### Frontend Setup
Navigate to root of `trails-viz-app`, install dependencies and start development server:
```shell script
$ cd trails-viz-app
$ npm install
$ npm run serve
```
This will start the server on port 8080. Navigate to http://localhost:8080.

Note: If you encounter `CORS` policy issues when viewing the dashboard on the development server, try different browsers. Firefox works, but Chrome and Safari may result in bugs.

## Build
Front end and back end has must be built separately. Run the following commands form the root of the project - `trails-viz`
```shell script
# build front end
$ cd trails-viz-app
$ npm run build
$ cd ..
# build back end
$ cd trails-viz-api
$ python setup.py bdist_wheel
```

This will create a `dist` folder in `trails-viz-app` with all the static html contents and 
`trailsvizapi-x.x.x-py3-none-any.whl` file in `trails-viz-api/dist` folder.

Now build the docker image from project root - `trails-viz`
```shell script
$ docker build -t trails-viz:latest .
``` 

## Running on Production
A conainer can be started from the docker image, which will run both the app and web inside it. To start the container, two 
arguments are required to run the app - the directory on the host which contains the csv and shape files must be 
mounted onto the container and environment variable `DATA_FILES_ROOT` must be set. Also host port must be mapped
if not using default.
```shell script
docker run -v <host-path-to-data>:/app/data-files \
-p 9000:80 \
-e DATA_FILES_ROOT=/app/data-files/ \
vivekkr12/trails-viz:latest
``` 
This will start the app on port 9000 on the host machine. If running behind a web server such as apache, the virtualhost 
can be configured to forward to the port.  This may require proxies for both the gui and the api.  On our production 
machine, we do this with:

```
ProxyPass /trails_site/ http://localhost:9000/
ProxyPassReverse /trails_site/ http://localhost:9000/
ProxyPass /api/ http://localhost:9000/api/
ProxyPassReverse /api/ http://localhost:9000/api/
```

## Adding a New Project
The instructions for adding a new project to the dashboard are documented [here](https://github.com/OutdoorRD/trails-viz/wiki/Adding-New-Project). 
