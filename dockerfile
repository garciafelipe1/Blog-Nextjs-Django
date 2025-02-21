FROM python:3.9

##install ssh client

RUN apt-get update && apt-get install -y openssh-client

#set enviroment variable
ENV PYTHONUNBUFFERED 1

#set work directory
WORKDIR /app

#copy requirements.txt

COPY requirements.txt /app/requirements.txt

#install dependencies
RUN pip install -r requirements.txt

#copy THE APP THE WORKING DIRECTORY

COPY . /app

#start the ssh tunel
CMD python manage.py runserver 0.0.0.0:8000