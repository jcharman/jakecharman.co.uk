FROM httpd:2.4 
RUN apt-get update
RUN apt-get -y install libapache2-mod-wsgi-py3 python3 python3-pip
COPY src/requirements.txt /var/www/jc/requirements.txt
RUN pip3 install  -r /var/www/jc/requirements.txt || pip3 install --break-system-packages -r /var/www/jc/requirements.txt
COPY --chown=www-data:www-data config/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY --chown=www-data:www-data src/ /var/www/jc
RUN httpd -t