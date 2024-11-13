FROM python:3.10
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/medfusion

WORKDIR /medfusion/

COPY backend /medfusion/backend
COPY agent /medfusion/agent
COPY poetry.lock pyproject.toml /medfusion/

RUN pip install poetry 
RUN poetry install --no-root
EXPOSE 8000