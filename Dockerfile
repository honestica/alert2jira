FROM python:3.12
WORKDIR /app

USER root

RUN pip3 install pipenv==2024.4.0
COPY Pipfile /app
COPY Pipfile.lock /app
RUN pipenv sync --clear --bare --system \
 && rm Pipfile Pipfile.lock

COPY src /app/src/
RUN useradd -m appuser \
 && chown -R appuser:appuser /app
 
USER appuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
