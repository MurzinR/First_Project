# Instructions copied from - https://hub.docker.com/_/python/
FROM python:3-onbuild

# tell the port number the container should expose
EXPOSE 5000

# run the command
ENV FLASK_APP main.py
RUN pip install pytest && pip install gunicorn
CMD bash -c "flask db upgrade && python main.py"