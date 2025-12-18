FROM python:3.14-slim
RUN python -m pip install hatch
RUN mkdir -p /app/
WORKDIR /app
COPY pyproject.toml /app

RUN hatch dep show requirements > /app/requirements.txt && \
  python -m pip install -r /app/requirements.txt

COPY ./src/emqx_client_monitor /app/src/emqx_client_monitor
COPY ./tests /app/tests
COPY ./README.md /app/README.md
RUN python -m pip install -e .

EXPOSE 9671

CMD ["emqx-client-monitor"]
