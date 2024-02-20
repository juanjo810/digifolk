# Instructions for Running Locally

## Install venv inside backend folder:

### mac/linux:
- cd backend
- python3.8 -m venv venv
- source venv/bin/activate
- pip3 install --upgrade pip
- pip3 install -r requirements.txt

### windows:
- cd backend
- py -3.8 -m venv venv
- & venv/Scripts/Activate.ps1
- py -3.8 -m pip install --upgrade pip
- py -3.8 -m pip install -r requirements.txt

## Run:

### migrations:
- alembic revision --autogenerate -m ""
- alembic upgrade head

### mac/linux:
- source venv/bin/activate
- python3 main.py

### windows:
- & venv/Scripts/Activate.ps1
- py -3.8 main.py

