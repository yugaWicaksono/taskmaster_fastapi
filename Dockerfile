FROM python:3.9-slim
ENV APP_HOME /taskmaster_api
WORKDIR $APP_HOME
COPY . ./

# remove testing variables
RUN cat .env
RUN sed -i '19,$d' .env
RUN cat .env

# --- RUN USING PIPENV ----

## RUN pip install pipenv
## RUN pipenv install -r requirements.txt
## RUN pipenv install --deploy --system

# Install production dependencies. according to gcloud
RUN pip3 install --no-cache-dir -r requirements.txt
# this has to use the shell insted of exec
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:api