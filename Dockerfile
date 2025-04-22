FROM ubuntu:22.04
LABEL maintainer="Cansin Acarer https://cacarer.com"
RUN apt-get -y update
RUN apt-get install --no-install-recommends -y python3.10 python3-dev python3-venv python3-pip python3-wheel build-essential libmysqlclient-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ADD . /mail-list-shield
WORKDIR /mail-list-shield
RUN pip install -r requirements.txt
EXPOSE 5000

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn","-b", "0.0.0.0:5000", "-w", "2", "-k", "gevent", "--worker-tmp-dir", "/dev/shm", "run:app", "--timeout", "1000"]
