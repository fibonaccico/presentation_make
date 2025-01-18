FROM rabbitmq:management
ENV RABBITMQ_DEFAULT_USER=your_username
ENV RABBITMQ_DEFAULT_PASS=your_password
WORKDIR /app
COPY . /app
RUN apt update \
     && apt install libreoffice --no-install-recommends -y \
     && apt install curl python3 -y \
     && apt install default-jre libreoffice-java-common -y \
#     && pip install poetry \
     && apt-get clean \
     && curl -sSL https://install.python-poetry.org | python3 - \
     && export PATH="/var/lib/rabbitmq/.local/bin:$PATH" \
     && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
     && rm -rf /var/lib/apt/lists/* \
     && poetry install --no-root --no-interaction --no-ansi \
#     && poetry cache list \
     && poetry cache clear PyPI --all --no-interaction
#rm -rf /root/.cache/pypoetry/virtualenvs/fibonacci-api-9TtSrW0h-py3.12/src \
#     && rm -rf /root/.cache/pypoetry/artifacts/*
ENV PATH="/var/lib/rabbitmq/.cache/pypoetry/virtualenvs/presentation-make-9TtSrW0h-py3.12/bin:$PATH"
VOLUME ["/app/presentations_images/"]
VOLUME ["/app/presentations_files/"]
VOLUME ["/app/log/"]
#COPY rabbitmq.conf /etc/rabbitmq/
EXPOSE 5672 15672
CMD ["rabbitmq-server"]
