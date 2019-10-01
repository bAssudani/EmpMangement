
import os
CONFIG_NAME = os.getenv('FLASK_CONFIG')

APP = os.name(CONFIG_NAME)

APP.run(ssl_context="adhoc")

if __name__ == '__main__':
    APP.run(debug=True)
