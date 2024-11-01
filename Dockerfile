FROM httpd:2.4 
COPY --chown=apache:apache src/ /usr/local/apache2/htdocs
