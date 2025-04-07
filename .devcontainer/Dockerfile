# This file sets up the Flask app container

FROM mcr.microsoft.com/devcontainers/python:3.11
LABEL maintainer="Cansin Acarer https://cacarer.com"
ADD .. /workspaces/base-saas
WORKDIR /workspaces/base-saas
EXPOSE 5000

# Install dependencies
RUN pip install -r requirements.txt

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1
