import os
import time

path = os.path.join(os.getcwd() + 'static/download/')

while True:
    now = time.time()

    for f in os.listdir(path):
        file = os.path.join(path, f)
        if os.stat(file).st_mtime < now - 7200:
            if os.path.isfile(file):
                os.remove(os.path.join(path, f))
    time.sleep(7500)
