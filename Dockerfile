FROM python:3.8-buster
LABEL maintainer="Mohammed Sunasra <sunasra.mh@pg.com>"

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip:
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# System deps:
RUN apt-get update &&\
    echo "deb https://deb.nodesource.com/node_14.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
    wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
    wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -yqq \
    nodejs \
    yarn \
    openssh-server \
    vim \
    curl \
    wget \
    telnet \
    tcptraceroute&& \
    pip install -U pip setuptools wheel && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8000 2222
ENV PORT 8000
ENV SSH_PORT 2222

# setup SSH
RUN mkdir -p /home/LogFiles \
    && echo "root:Docker!" | chpasswd \
    && echo "cd /home" >> /etc/bash.bashrc
COPY sshd_config /etc/ssh/

WORKDIR /app
RUN mkdir -p media

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app/app
COPY app/yarn.lock app/package.json ./
RUN yarn install --frozen-lockfile

WORKDIR /app
COPY . .
RUN chmod u+x entrypoint.sh pre-deploy.sh
RUN pip install -e .
RUN manage collectstatic -i pcss -i node_modules -i app/src --noinput

WORKDIR /app/app
RUN NODE_ENV=production yarn build

WORKDIR /app
CMD [ "./entrypoint.sh" ]
