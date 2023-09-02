FROM resin/rpi-raspbian:latest
FROM python:3.9-slim-buster

WORKDIR /app

COPY ./requirements.txt /app

RUN pip3 install Flask
RUN pip install -r requirements.txt
RUN apt update
RUN apt install python3-pip -y


COPY . .

ENV FLASK_APP=app.py

CMD ["sh","-c","sleep 7 && gunicorn --bind 0.0.0.0:80 wsgi:app --workers 2"]

#,"","1"]



#    Import python from dockerhub.
#    Create a working directory app.
#    Copy the requirements.txt file inside the app directory.
#    Install all the dependencies from the requirements.txt file.
#    Copy the entire app project into the app directory.
#    We expose port 5000 as the app will run on port 5000.
#    Define the FLASK_APP environment variable. Else the interpreter may complain it’s unable to find the variable
#    Finally, type in the run command which is flask run --host 0.0.0.0. This is to ensure the server accepts requests from all hosts.