from main import app
from blueprints.config import METHOD, PORT_LOCAL, PORT_PUBLIC, DEBUG_MODE, PUBLIC_IP, LOCAL_IP

##### RUN APP #####
if __name__ == "__main__":
    if METHOD == 'device':
        app.run(port=PORT_LOCAL, debug=DEBUG_MODE)
    elif METHOD == 'local':
        app.run(host=LOCAL_IP, port=PORT_LOCAL, debug=DEBUG_MODE)
    elif METHOD == 'public':
        app.run(host=PUBLIC_IP, port=PORT_PUBLIC, debug=DEBUG_MODE)