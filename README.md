# BITE - A Basic/IoT/Example

Playing with IoT

[![Build Status](https://travis-ci.com/daniviga/bite.svg?branch=master)](https://travis-ci.com/daniviga/bite)
![AGPLv3](./docs/.badges/agpl3.svg)
![Python 3.8](./docs/.badges/python.svg)
![MQTT](./docs/.badges/mqtt.svg)
![Moby](./docs/.badges/moby.svg)
![docker-compose 3.7+](./docs/.badges/docker-compose.svg)

This project is for educational purposes only. It does not implement any
authentication and/or encryption protocol, so it is not suitable for real
production.

![Application Schema](./docs/application_chart.png)

### Future implementations

- Broker HA via [VerneMQ clustering](https://docs.vernemq.com/clustering/introduction)
- Stream analytics via [Apache Spark](https://spark.apache.org/)

## Installation

### Requirements

- `docker-ce` or `moby`
- `docker-compose`

The project is compatible with Docker for Windows (using Linux executors),
but it is advised to directly use a minimal Linux VM instead
(via the preferred hypervisor).

The application stack is composed by the following components:

- [Django](https://www.djangoproject.com/) with
[Django REST framework](https://www.django-rest-framework.org/)
web application (running via `gunicorn` in production mode)
  - `mqtt-to-db` custom daemon to dump telemetry into the timeseries database
  - telemetry payload is stored as json object (via PostgreSQL JSON data type)
- [Timescale](https://www.timescale.com/) DB,
a [PostgreSQL](https://www.postgresql.org/) database with a timeseries extension
- [Mosquitto](https://mosquitto.org/) MQTT broker (see alternatives below)
- [Nginx](http://nginx.org/) as ingress for HTTP (see alternative below)
- [Chrony](https://chrony.tuxfamily.org/) as NTP server
(with optional `MD5` encryption)

## Deployment

The `$CUSTOM_DOCKER_IP` environment variable can be used to set a custom
IP address to bind ports. Default is `0.0.0.0`; `127.0.0.1` is a
safe configuration (see https://github.com/docker/compose/issues/2999).

### Development, using image code

```bash
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d [--scale {bite,mqtt-to-db)=N]
```
It exposes:

- `http://localhost:80` (HTTP and MQTT over Websockets)
- `tcp://localhost:1883` (MQTT)
- `udp://localhost:123` (NTP)

Django runs with `DEBUG = True` and `SKIP_WHITELIST = True`

### Development with direct access to services and autoreload

```bash
docker-compose -f docker/docker-compose.yml -f docker-compose.dev.yml up -d [--scale {bite,mqtt-to-db)=N]
```

It exposes:

- `http://localhost:80` (HTTP and MQTT over Websockets)
- `http://localhost:8080` (Django's `runserver`)
- `tcp://localhost:1883` (MQTT)
- `tcp://localhost:9001` (MQTT over Websockets)
- `udp://localhost:123` (NTP)
- `tcp://localhost:5432` (PostgreSQL/Timescale)

Django runs with `DEBUG = True` and `SKIP_WHITELIST = True`

### Production (kind of...)

```bash
docker-compose -f docker/docker-compose.yml -f docker-compose.prod.yml up -d [--scale {bite,mqtt-to-db)=N]
```
It exposes:

- `http://localhost:80` (HTTP and MQTT over Websockets)
- `tcp://localhost:1883` (MQTT)
- `udp://localhost:123` (NTP)

Django runs with `DEBUG = False` and `SKIP_WHITELIST = False`

## Extra features

The project provides multiple modules that can be combined with the fore-mentioned configurations.

### Traefik

To use [Traefik](https://containo.us/traefik/) instead of Nginx use:
```bash
docker-compose -f docker/docker-compose.yml up -f docker/ingress/docker-compose.traefik.yml -d
```

### VerneMQ

A ~8x memory usage can be expected compared to Mosquitto.

To use [VerneMQ](https://vernemq.com/) instead of Mosquitto run:
```bash
docker-compose -f docker/docker-compose.yml up -f docker/mqtt/docker-compose.vernemq.yml -d
```

### RabbitMQ

RabbitMQ does provide AMQP protocol too, but ingestion on the application side
is not implemented yet.
A ~10x memory usage can be expected compared to Mosquitto.

To use [RabbitMQ](https://www.rabbitmq.com/) (with the MQTT plugin enabled)
 instead of Mosquitto run:

```bash
docker-compose -f docker/docker-compose.yml up -f docker/mqtt/docker-compose.rabbitmq.yml -d
```

## EDGE gateway simulation (via dind)

An EDGE gateway, with containers as modules, may be simulated via dind
(docker-in-docker).

### Start the EDGE

```bash
docker-compose -f docker/docker-compose.yml up -f docker/edge/docker-compose.edge.yml -d
```

### Run the modules inside the EDGE

```bash
DOCKER_HOST='127.0.0.1:22375' docker-compose -f docker-compose.modules.yml up -d [--scale {device-http,device-ws,device-mqtt}=N]
```

## Arduino

A simple Arduino UNO sketch is provided in the `arduino/tempLightSensor` folder.
The sketch reads temperature and light from sensors.

```c
/* ... */

void loop(void) {
  const int postDelay = TELEMETRY_DELAY * 1000;

  unsigned int tempReading = analogRead(A0);
  unsigned int photocellReading = analogRead(A1);

  float tempVoltage = tempReading * AREF_VOLTAGE / 1024.0;
  float tempC = (tempVoltage - 0.5) * 100 ;

  if (NTPValid) {
    telemetry["clock"] = timeClient.getEpochTime();
  } else {
    telemetry["clock"] = NULL; // converted into 0
  }
  payload["light"] = photocellReading;

  temp["celsius"] = tempC;
  temp["raw"] = tempReading;
  temp["volts"] = tempVoltage;

#if USE_MQTT
  publishData(config, telemetry);
#else
  postData(config, telemetryURL, telemetry);
#endif

/* ... */
```

[Read more ...](./arduino/README.md)

## Testing

Application tests are part of the Django suite:

```bash
python manage.py test
```

End-to-End tests are performed via Travis-CI. See [`.travis.yml`](.travis.yml)
for further explanations.
