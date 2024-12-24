FROM python:3.10

WORKDIR /medfusion

COPY backend /medfusion/backend
COPY agent /medfusion/agent
COPY pyproject.toml /medfusion/

RUN pip install poetry
RUN poetry install

# RUN poetry install --no-root
# RUN poetry shell

RUN poetry run python -m backend.src.migration.main --action create
EXPOSE 8000

CMD poetry run python -m backend.src.main
