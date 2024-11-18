# first thing that has to be performed is pip install -r /app/shared/requirements.txt
# then run flask on port 5000 and host 0.0.0.0

#!/bin/bash

pip install -r /app/shared/requirements.txt
flask run --host=0.0.0.0 --port=5000