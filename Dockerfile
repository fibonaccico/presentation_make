FROM python:3.11
WORKDIR /app
COPY . /app
RUN apt update \
     && apt install libreoffice --no-install-recommends -y \
     && apt install curl python3 -y \
     && apt install default-jre libreoffice-java-common -y  \
     && apt-get install -y traceroute iproute2 inetutils-ping \
     && apt-get clean \
     && curl -sSL https://install.python-poetry.org | python3 - \
     && export PATH="/root/.local/bin:$PATH" \
     && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
     && rm -rf /var/lib/apt/lists/* \
     && poetry install --no-root --no-interaction --no-ansi \
     && poetry cache list \
     && poetry cache clear PyPI --all --no-interaction \
#rm -rf /root/.cache/pypoetry/virtualenvs/fibonacci-api-9TtSrW0h-py3.12/src \
     && rm -rf /root/.cache/pypoetry/artifacts/*
ENV PATH="/root/.cache/pypoetry/virtualenvs/presentation-make-9TtSrW0h-py3.11/bin:$PATH"
VOLUME ["/app/presentations_images/"]
VOLUME ["/app/presentations_files/"]
VOLUME ["/app/log/"]
#COPY rabbitmq.conf /etc/rabbitmq/
#EXPOSE 5672 15672
#CMD ["python /app/consumer.py"]
#CMD ["python", "/app/consumer.py"]
CMD sh -c "ip route add 195.242.11.3 via 172.29.0.2 && ip route add 149.154.166.110 via 172.29.0.2 && python /app/consumer.py"
