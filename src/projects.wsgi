#!/usr/bin/python3

import sys
sys.path.append('/var/www/jc')

from index import app as application

if __name__ == '__main__':
    application.run(debug=True)