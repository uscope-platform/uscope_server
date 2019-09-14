from app_factory import create_app

import sys

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "DBG":
        app = create_app(debug=True)
    else:
        app = create_app(debug=False)

    app.run(host='0.0.0.0', threaded=True, port=4998)
