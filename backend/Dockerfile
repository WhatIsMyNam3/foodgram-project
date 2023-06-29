FROM python:3.7-slim
RUN mkdir /app
COPY requirements.txt /app
RUN pip install --upgrade pip && pip3 install -r /app/requirements.txt --no-cache-dir 
COPY . /app
WORKDIR /app
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "collectstatic", "--noinput"]
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]