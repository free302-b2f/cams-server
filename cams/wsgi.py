"""WSGI application gateway"""

print(f"<{__name__}> loading...")

import sys
from main import app, debug, getSettings

# ---- [set TEST mode On/Off] ----
setattr(sys, "_test_", getSettings("Cams", "SetTestMode"))


application = app.server

if __name__ == "__main__":

    # debug("running app.run_server()...")
    print("running app.run_server()...")
    app.run_server(debug=True, port=28050, host="0.0.0.0", use_reloader=False)
