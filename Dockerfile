FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy
COPY . .

EXPOSE 8000

CMD [ "gunicorn", "run:app", "-w", "4", "-b", "0.0.0.0:8000" ]
