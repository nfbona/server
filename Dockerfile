FROM resin/rpi-raspbian:latest 
FROM python:3.9-slim-buster as base

# copy all necessary files into workdirectory
COPY ./static /app/static
COPY ./Modules /app/Modules
COPY ./templates /app/templates
COPY ./website /app/website
COPY ./app.py /app/app.py
COPY ./.env /app/.env
COPY ./wsgi.py /app/wsgi.py
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app


RUN pip3 install Flask
RUN pip install -r requirements.txt

ENV FLASK_APP=app.py

#DEUBUG
FROM base as dev

RUN pip install debugpy

CMD python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m gunicorn --bind 0.0.0.0:80 wsgi:app --workers 1 --threads 5 --worker-class=sync

# PRODUCTION
FROM base as production

CMD ["sh","-c","sleep 0 && gunicorn --bind 0.0.0.0:80 wsgi:app --workers 1 --threads 5 --worker-class=sync"]

#,"","1"]



#    Import python from dockerhub.
#    Create a working directory app.
#    Copy the requirements.txt file inside the app directory.
#    Install all the dependencies from the requirements.txt file.
#    Copy the entire app project into the app directory.
#    We expose port 5000 as the app will run on port 5000.
#    Define the FLASK_APP environment variable. Else the interpreter may complain it’s unable to find the variable
#    Finally, type in the run command which is flask run --host 0.0.0.0. This is to ensure the server accepts requests from all hosts.