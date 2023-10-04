FROM python:3.9-slim-buster

WORKDIR /app

RUN python -m venv venv
RUN . venv/bin/activate

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

EXPOSE 5002

CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]