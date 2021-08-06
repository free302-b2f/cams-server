# -*- coding: utf-8 -*-

import sys
print(f'{sys.path = }')

from index import app
application = app.server

if __name__ == '__main__':
    print('running app.run_server()...')
    app.run_server(debug=True, port=27111, host='0.0.0.0')
