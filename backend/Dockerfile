FROM python:3.7-slim
RUN mkdir /app
COPY . /app
RUN pip install --upgrade pip && pip3 install -r /app/requirements.txt --no-cache-dir 
WORKDIR /app
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]