FROM python:3.11

WORKDIR /app
COPY . /app
RUN apt update
RUN apt install libreoffice --no-install-recommends -y \
     && apt install curl -y \
     && apt install default-jre libreoffice-java-common -y \
     && apt-get clean \
     && curl -sSL https://install.python-poetry.org | python3 - \
     && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
     && rm -rf /var/lib/apt/lists/* \
     && poetry install --no-root --no-interaction --no-ansi \
     && poetry cache list \
     && poetry cache clear PyPI --all --no-interaction \
#rm -rf /root/.cache/pypoetry/virtualenvs/fibonacci-api-9TtSrW0h-py3.12/src \
     && rm -rf /root/.cache/pypoetry/artifacts/*
VOLUME ["/app/presentations_images/"]
VOLUME ["/app/presentations_files/"]
VOLUME ["/app/log/"]
EXPOSE 5672
#ENV PATH="/root/.cache/pypoetry/virtualenvs/fibonacci-api-9TtSrW0h-py3.12/bin:$PATH"
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
