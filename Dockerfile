FROM python:3.14-bookworm
RUN apt-get update
RUN apt-get -y install apache2 apache2-dev
COPY src/requirements.txt /var/www/jc/requirements.txt
RUN /usr/local/bin/pip3 install --upgrade pip
RUN /usr/local/bin/pip3 install  -r /var/www/jc/requirements.txt
COPY --chown=www-data:www-data config/httpd.conf /etc/apache2/apache2.conf
COPY --chown=www-data:www-data src/ /var/www/jc
RUN apache2 -t
EXPOSE 80
ENTRYPOINT ["apache2", "-D", "FOREGROUND"]