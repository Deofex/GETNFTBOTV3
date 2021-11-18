# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set time zone
ENV TZ=Europe/Amsterdam
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y cron
RUN rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY /UpcomingEventsReport/requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY /UpcomingEventsReport /app
COPY /modules /modules

# Add modules to pythonpath
ENV PYTHONPATH "${PYTHONPATH}:/modules"
# Make run.sh executable
RUN chmod +x run.sh

# Add entrypoint
ENTRYPOINT ["/app/run.sh"]
