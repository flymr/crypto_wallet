FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN mkdir /code/static
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
ENTRYPOINT ["/code/entrypoint.sh"]
