FROM nginx:1.17.4

RUN apt-get update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install dos2unix
RUN pip3 install uwsgi

COPY docker-conf/nginx.conf /etc/nginx/nginx.conf
COPY docker-conf/default.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /app/logs

COPY trails-viz-app/dist /usr/share/nginx/html
COPY trails-viz-api/uwsgi-config.ini /app/uwsgi-config.ini
COPY docker-conf/start.sh /app/start.sh

COPY trails-viz-api/dist/trailsvizapi-*-py3-none-any.whl /app/

RUN dos2unix /app/start.sh
RUN chmod 755 /app/start.sh
RUN cd /app && whl_file=`ls | grep whl` && pip3 install $whl_file && cd ..

WORKDIR /app

EXPOSE 80 443

CMD ["/bin/bash", "./start.sh"]
