FROM python:3.10.6

RUN groupadd --gid 1000 appuser \
    && useradd --home-dir /home/appuser --create-home --uid 1000 \
        --gid 1000 --shell /bin/sh --skel /dev/null appuser
RUN apt-get update && apt-get -y install nano

WORKDIR /src

COPY poetry.lock pyproject.toml /src/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

COPY --chown=appuser . /src

EXPOSE 5002

RUN chown -R appuser.appuser /var /run /src /tmp

ENTRYPOINT ["poetry", "run"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5002", "--reload"]

