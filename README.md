# Django Site

Докеризированный сайт на Django для экспериментов с Kubernetes.

Внутри контейнера Django приложение запускается с помощью Nginx Unit, не путать с Nginx. Сервер Nginx Unit выполняет сразу две функции: как веб-сервер он раздаёт файлы статики и медиа, а в роли сервера-приложений он запускает Python и Django. Таким образом Nginx Unit заменяет собой связку из двух сервисов Nginx и Gunicorn/uWSGI. [Подробнее про Nginx Unit](https://unit.nginx.org/).

## Как подготовить окружение к локальной разработке

Код в репозитории полностью докеризирован, поэтому для запуска приложения вам понадобится Docker. Инструкции по его установке ищите на официальных сайтах:

- [Get Started with Docker](https://www.docker.com/get-started/)

Вместе со свежей версией Docker к вам на компьютер автоматически будет установлен Docker Compose. Дальнейшие инструкции будут его активно использовать.

## Как запустить сайт для локальной разработки

Запустите базу данных и сайт:

```shell
$ docker compose up
```

В новом терминале, не выключая сайт, запустите несколько команд:

```shell
$ docker compose run --rm web ./manage.py migrate  # создаём/обновляем таблицы в БД
$ docker compose run --rm web ./manage.py createsuperuser  # создаём в БД учётку суперпользователя
```

Готово. Сайт будет доступен по адресу [http://127.0.0.1:8080](http://127.0.0.1:8080). Вход в админку находится по адресу [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Как вести разработку

Все файлы с кодом django смонтированы внутрь докер-контейнера, чтобы Nginx Unit сразу видел изменения в коде и не требовал постоянно пересборки докер-образа -- достаточно перезапустить сервисы Docker Compose.

### Как обновить приложение из основного репозитория

Чтобы обновить приложение до последней версии подтяните код из центрального окружения и пересоберите докер-образы:

``` shell
$ git pull
$ docker compose build
```

После обновлении кода из репозитория стоит также обновить и схему БД. Вместе с коммитом могли прилететь новые миграции схемы БД, и без них код не запустится.

Чтобы не гадать заведётся код или нет — запускайте при каждом обновлении команду `migrate`. Если найдутся свежие миграции, то команда их применит:

```shell
$ docker compose run --rm web ./manage.py migrate
…
Running migrations:
  No migrations to apply.
```

### Как добавить библиотеку в зависимости

В качестве менеджера пакетов для образа с Django используется pip с файлом requirements.txt. Для установки новой библиотеки достаточно прописать её в файл requirements.txt и запустить сборку докер-образа:

```sh
$ docker compose build web
```

Аналогичным образом можно удалять библиотеки из зависимостей.

<a name="env-variables"></a>
## Переменные окружения

Образ с Django считывает настройки из переменных окружения:

`SECRET_KEY` -- обязательная секретная настройка Django. Это соль для генерации хэшей. Значение может быть любым, важно лишь, чтобы оно никому не было известно. [Документация Django](https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key).

`DEBUG` -- настройка Django для включения отладочного режима. Принимает значения `TRUE` или `FALSE`. [Документация Django](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-DEBUG).

`ALLOWED_HOSTS` -- настройка Django со списком разрешённых адресов. Если запрос прилетит на другой адрес, то сайт ответит ошибкой 400. Можно перечислить несколько адресов через запятую, например `127.0.0.1,192.168.0.1,site.test`. [Документация Django](https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts).

`DATABASE_URL` -- адрес для подключения к базе данных PostgreSQL. Другие СУБД сайт не поддерживает. [Формат записи](https://github.com/jacobian/dj-database-url#url-schema).


## Kubernetes

Работа сайта также возможна в кластере Kubernetes

### Предварительная подготовка
Для запуска в тестовом режиме вам понадобятся [kubectl](https://kubernetes.io/ru/docs/tasks/tools/install-kubectl/), а также 
[Minikube](https://kubernetes.io/ru/docs/tasks/tools/install-minikube/). 

### Kubernetes Environment

Создайте `.env` файл в корне проекта и задайте в нем переменные указанные выше.  
Для создания манифеста с вашим secret выполните:

```shell
python3 local-minikube-virtualbox/secret.py
```
Если какие-либо значения изменятся, требуется повторно выполнить данную команду.

### Создание кластера

Выполните команды:

```shell
 kubectl apply -f local-minikube-virtualbox/k8s
 kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

Для выполнения миграции выполните команду:

```shell
kubectl apply -f local-minikube-virtualbox/k8s/django-migrate-job.yaml
```

#### Minikube

При работе в Minikube выполните команду:

```shell
minikube addons enable ingress
```

Добавьте в ваш файл `hosts` пару - ip адрес вашей виртуальной машины и домен `star-burger.test`. 
[Инструкция по добавлению](https://help.reg.ru/support/dns-servery-i-nastroyka-zony/rabota-s-dns-serverami/fayl-hosts-gde-nakhoditsya-i-kak-yego-izmenit).  
Для получения Ip адреса выполните команду:
```shell
minikube ip
```

### Развертывание в Yandex Cloud
Данный подразумевает, что у вас имеется доступ к необходимым сервисам [Yandex Cloud](https://cloud.yandex.ru/).

#### Развертывание тестового сервиса

У вас должен быть создан Application Load Balancer. В приведенном нижее манифесте используется порт `30401` с 
разворачиваемым сервисом `nginx`.

```shell
 kubectl apply -f test-nginx-edu-angry-sammet
```

### Как подготовить dev окружение

PostgreSQL-хосты с публичным доступом поддерживают только шифрованные соединения. 
Чтобы использовать их, получите SSL-сертификат:

```shell
mkdir -p ~/.postgresql && \
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
     --output-document ~/.postgresql/root.crt && \
chmod 0600 ~/.postgresql/root.crt
```

Сертификат будет сохранен в файле ~/.postgresql/root.crt. 
[Подробнее](https://cloud.yandex.ru/ru/docs/managed-postgresql/operations/connect#get-ssl-cert)

Скопируйте `root.crt` в корневую дирректорию репозитория. Выполните команду: 

```shell
python3 cert_secret.py
```

Будет создан секрет в вашем k8s.