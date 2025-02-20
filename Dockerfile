# using lightwegith alpine docker linux image of python
FROM python:3.9-alpine3.13 
# the one who is the maintainer of the app
LABEL maintainer="rehman.abdur@devsinc.com"
# means the output of the application will be seen directly on the screen with out any buffer
ENV PYTHONUNBUFFERED 1
# copy current directory file into docker image
COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
# defining working directory so everytime we dont need to set path before running command, it will be run directly from app.
WORKDIR /app 
# exposing port 8000 from our container to our machine 
EXPOSE 8000
#installig some dependencies

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser\
    --disabled-password \
    --no-create-home \
    django-user
    
ENV PATH="/py/bin:$PATH"
# all above will be run by root user, but once created django-user we will switch our image to django-user that have not all root preveliges.
USER django-user

