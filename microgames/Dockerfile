FROM python:3.11.3-slim-buster

WORKDIR /code

ARG UID=1000
ARG GID=1000
ARG PWD=${PWD:-/code}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/code

RUN apt update && apt install curl -y
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    chmod 755 /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /code/

RUN chown -R "$UID:$GID" "${PWD}" && \
     id "$UID" || \
     useradd -m -u "$UID" docker

RUN bash -c "poetry install --no-root --no-dev"

COPY ./src /code
USER ${UID}:${GID}
EXPOSE 50051
