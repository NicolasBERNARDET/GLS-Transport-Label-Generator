FROM alpine:latest

RUN apk --no-cache add python3 py3-pip

WORKDIR /app

COPY ../requirements.txt ./

RUN apk update RUN  apk add  gcc g++ unixodbc-dev python3-dev curl bash sudo

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add
RUN  curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN  apt-get update
RUN  ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt-get install -y  msodbcsql17  unixodbc-dev

RUN  rm -rf /var/lib/apt/lists/*

RUN  touch /usr/share/locale/locale.alias
RUN  sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen RUN  locale-gen

RUN pip install -r requirements.txt

COPY /app /app

EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]