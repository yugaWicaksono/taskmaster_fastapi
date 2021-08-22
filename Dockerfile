FROM python:3.7-slim
ENV APP_HOME /taskmaster_api
WORKDIR $APP_HOME
COPY . ./
RUN pip install pipenv
RUN pipenv install -r requirements.txt
RUN pipenv install --deploy --system
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app.main:api