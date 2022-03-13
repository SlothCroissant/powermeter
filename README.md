# [SlothCroissant/powermeter](https://github.com/SlothCroissant/powermeter)

[![GitHub Build Status](https://img.shields.io/github/workflow/status/slothcroissant/powermeter/Docker%20Image%20CI/nightly?style=for-the-badge)](https://github.com/SlothCroissant/powermeter/actions/workflows/docker_build.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/slothcroissant/rpi-powermeter?style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-powermeter)
[![Docker Stars](https://img.shields.io/docker/stars/slothcroissant/rpi-powermeter?style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-powermeter)
[![Docker Image Size](https://img.shields.io/docker/image-size/slothcroissant/rpi-powermeter?style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-powermeter)
[![Docker Image Version](https://img.shields.io/docker/v/slothcroissant/rpi-powermeter?sort=semver&style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-powermeter)
[![License](https://img.shields.io/github/license/slothcroissant/powermeter?style=for-the-badge)]

## Overview

[SlothCroissant/powermeter](https://github.com/SlothCroissant/powermeter) is an open-source energy meter implementation for the Raspberry Pi platform, written in Python. Hardware specifications can be found in the `/hardware` folder. The application can be run either natively via Python, or the available Docker container.

At a high-level, the application reads voltage values via [SPI](https://wikipedia.org/wiki/Serial_Peripheral_Interface) from split-core [current transformers](https://en.wikipedia.org/wiki/Current_transformer) (commonly referred to as CTs, and are made by a variety of manufacturers such as [YHDC](https://en.yhdc.com/product/SCT013-401.html)), converts the values to watts, and writes the resulting data to a MySQL/MariaDB database.

## Minimum Requirements

There are very few requirements from the hardware/OS perspective:

* [Raspberry Pi 3b+ or higher](https://www.raspberrypi.org/) (Inclding all models of the Raspberry Pi 4)
* Latest [Raspberry Pi OS](https://www.raspberrypi.com/software/) installed
* An existing MySQL or Maria Database deployed and accessible from the Raspberry Pi. Note: due to MicroSD card wear, it is not recommended to run the DB on the Raspberry Pi itself.

## Running via Docker

Here are the quick steps to get up and running on Docker with your freshly-installed Raspberry Pi OS:
mo
1. Install `docker-ce` (or ensure you are on the latest version of `docker-ce` - tested on `20.10.13`)
1. Run the docker container with any of the options noted below.

## Available Container Registries

If deploying via Docker, users can choose whichever container registry they prefer - we will continuously deploy to both:

* Docker Hub: [slothcroissant/powermeter]((https://hub.docker.com/r/slothcroissant/rpi-powermeter))
* GitHub Container Registry: [ghcr.io/slothcroissant/powermeter](https://github.com/SlothCroissant/powermeter/pkgs/container/rpi-powermeter)

## Version Tags

This image provides various versions that are available via tags. `nightly` tag usually provides the latest testing version until production-ready. There are also dated tags to pull specific snapshots in development (Example: `2022.03.12.3`).

| Tag | Description |
| ---- | --- |
| nightly | Latest testing release |
| YYYY.MM.DD.## | Specific snapshot testing release |

## Usage

Here are some example snippets to help you get started creating a container.

### docker-compose (recommended, [click here for more info](https://docs.docker.com/compose/compose-file/compose-file-v3/))

```yaml
version: '3.8'

services:
  powermeter:
    container_name: powermeter
    image: slothcroissant/rpi-powermeter:nightly
    environment:
      - ct0=20
      - ct1=20
      - ct2=20
      - ct3=20
      - ct4=20
      - ct5=20
      - ct6=20
      - ct7=30
      - db_host=dbhost.lan
      - db_port=3306
      - db_database=data
      - db_table=powermeter
      - db_user=dbuser
      - db_pass=dbpassword
    devices:
      - /dev/spidev0.0
```

### docker cli ([click here for more info](https://docs.docker.com/engine/reference/commandline/cli/))

```bash
docker run -d \
  --name=powermeter \
  --device=/dev/spidev0.0 \
  -e ct0=20 \
  -e ct1=20 \
  -e ct2=20 \
  -e ct3=20 \
  -e ct4=20 \
  -e ct5=20 \
  -e ct6=20 \
  -e ct7=30 \
  -e db_host="dbhost.lan" \
  -e db_port=3306 \
  -e db_database="data" \
  -e db_table="powermeter" \
  -e db_user="dbuser" \
  -e db_pass="dbpassword" \
  --restart unless-stopped \
  slothcroissant/rpi-powermeter:nightly
```

## Environment Variables

When running the `docker run` command, the Docker CLI client checks the value the variable has in your local environment and passes it to the container. If no `=` is provided and that variable is not exported in your local environment, the variable won’t be set in the container.

| Env Var | Function |
| ---- | --- |
| `-e ctX=YY` | Set the amperage rating YY for ct X. You can find this directly on the CT clamp itself if needed |
| `-e db_host="dbhost.lan"` | Hostname or IP address for your existing MySQL/MariaDB host |
| `-e db_port=3306` | TCP port for your existing MySQL/MariaDB host |
| `-e db_database="data"` | Database name for your existing MySQL/MariaDB host |
| `-e db_table="powermeter"` | Table name for your existing MySQL/MariaDB host |
| `-e db_user="dbuser"` | Database username for your existing MySQL/MariaDB host, which has appropriate access to `db_database` |
| `-e db_pass="dbpassword"` | Database user password for your existing MySQL/MariaDB host, which has appropriate access to `db_database` |