FROM python:3.9.10-alpine

# Установка локальных переменныхp
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/gooru
WORKDIR /usr/src/gooru
COPY . .


# Установка зависимостей для Django
RUN apk update \
    && apk add postgresql \
    && apk add postgresql-dev \
    && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev \
    && apk add jpeg-dev zlib-dev libjpeg libffi-dev
#     && pip install Pillow \
#     && apk del build-deps

RUN apk add make automake gcc g++ subversion python3-dev
# ENV LANG C.UTF-8
# ENV LC_ALL C.UTF-8

CMD python3 --version
CMD . env/bin/activate

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/usr/src/gooru/entrypoint.sh"]


