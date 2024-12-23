FROM python:3.10

WORKDIR /medfusion

COPY backend /medfusion/backend
COPY agent /medfusion/agent
COPY pyproject.toml /medfusion/

RUN pip install poetry
RUN poetry install --no-root

EXPOSE 8000

CMD poetry run python -m backend.src.main
