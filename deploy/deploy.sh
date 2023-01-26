#!/usr/bin/bash

# cd to project directory
cd "$(dirname "$1")"/.. || exit

# Create virtual environment if it does not exist.
if [ ! -d venv ]; then
  echo "Virtual environment does not exist, creating virtual environment..."
  pip3 install virtualenv
  python3 -m virtualenv venv
fi

# activate virtualenv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run server
gunicorn --chdir api server:app