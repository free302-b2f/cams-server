"""WSGI application gateway"""

import sys

print(f"{sys.path = }")

from main import app, debug

application = app.server


if __name__ == "__main__":
    debug("running app.run_server()...")
    app.run_server(debug=True, port=28050, host="0.0.0.0", use_reloader=False)
