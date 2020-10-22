FROM python:3.8.5
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
EXPOSE 5000
RUN pip install -r requirements.txt
CMD ["gunicorn","-b 0.0.0.0:5000", "wsgi:app"]
