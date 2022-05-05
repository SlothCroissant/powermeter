# [SlothCroissant/rpi-energymeter](https://github.com/SlothCroissant/rpi-energymeter)

[![GitHub Build Status](https://img.shields.io/github/workflow/status/slothcroissant/rpi-energymeter/Docker%20Image%20CI/nightly?style=for-the-badge)](https://github.com/SlothCroissant/rpi-energymeter/actions/workflows/docker_build.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/slothcroissant/rpi-energymeter?style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-energymeter)
[![Docker Stars](https://img.shields.io/docker/stars/slothcroissant/rpi-energymeter?style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-energymeter)
[![Docker Image Size](https://img.shields.io/docker/image-size/slothcroissant/rpi-energymeter?style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-energymeter)
[![Docker Image Version](https://img.shields.io/docker/v/slothcroissant/rpi-energymeter?sort=semver&style=for-the-badge)](https://hub.docker.com/r/slothcroissant/rpi-energymeter)
[![License](https://img.shields.io/github/license/slothcroissant/rpi-energymeter?style=for-the-badge)]

## Overview

[SlothCroissant/rpi-energymeter](https://github.com/SlothCroissant/rpi-energymeter) is an open-source energy meter implementation for the Raspberry Pi platform, written in Python. Hardware specifications can be found in the following repo: (`repo TBD`). The application can be run either natively via Python, or the available Docker container.

At a high-level, the application reads voltage values via [SPI](https://wikipedia.org/wiki/Serial_Peripheral_Interface) from split-core [current transformers](https://en.wikipedia.org/wiki/Current_transformer) (commonly referred to as CTs, and are made by a variety of manufacturers such as [YHDC](https://en.yhdc.com/product/SCT013-401.html)), converts the values to watts, and exposes the results via a Python Flask REST endpoint. Users can then consume the data into whichever database, etc software they choose.

## Prerequisites

There are very few prerequisites the hardware/OS perspective:

* [Raspberry Pi 3b+ or higher](https://www.raspberrypi.org/) (Inclding all models of the Raspberry Pi 4)
* Latest [Raspberry Pi OS](https://www.raspberrypi.com/software/) installed

## Running via Docker

Here are the quick steps to get up and running on Docker with your freshly-installed Raspberry Pi OS:
mo
1. Install `docker-ce` (or ensure you are on the latest version of `docker-ce` - tested on `20.10.13`)
1. Run the docker container with any of the options noted below.

## Available Container Registries

If deploying via Docker, users can choose whichever container registry they prefer - we will continuously deploy to both:

* Docker Hub: [slothcroissant/rpi-energymeter]((https://hub.docker.com/r/slothcroissant/rpi-energymeter))
* GitHub Container Registry: [ghcr.io/slothcroissant/rpi-energymeter](https://github.com/SlothCroissant/rpi-energymeter/pkgs/container/rpi-energymeter)

## Version Tags

This image provides various versions that are available via tags. `nightly` tag usually provides the latest testing version until production-ready. There are also dated tags to pull specific snapshots in development (Example: `2022.03.12.3`).

| Tag | Description |
| ---- | --- |
| `nightly` | Latest testing release |
| `YYYY.MM.DD.##` | Specific snapshot testing release |

**Note:** The `nightly` branch is under heavy development. It can break at any time, without warning. Consequently, please be sure you fully review changes between your deployed version's `README.md` and the current to ensure we haven't introduced breaking changes with environment variables, etc.

## Usage

First off, determine your CT amperage ratings across all mux channels you have deployed. For example (and in the docker examples below) I have 16 CTs spread across two mux channels with varying CT amperage ratings. The CTs and mux channels are both numbered 0-7, and you'd denote a certain CT by using the following idea:

`ct<mux_channel>_<ct_number>`

So some quick examples:

* `ct0_1` would be mux channel 0 (the first mux channel on the board), CT number 1 (the second CT on the board). 
* `ct1_7` indicates mux_channel 1 (the second mux channel) and CT 7 (the 8th and final CT on that mux channel)

Here are some example snippets to help you get started creating a container:

### docker-compose (recommended, [click here for more info](https://docs.docker.com/compose/compose-file/compose-file-v3/))

```yaml
version: '3.8'

services:
  energymeter:
    container_name: energymeter
    image: slothcroissant/rpi-energymeter:nightly
    restart: always
    environment:
    - ct0_0=100
    - ct0_1=100
    - ct0_2=30
    - ct0_3=30
    - ct0_4=20
    - ct0_5=20
    - ct0_6=20
    - ct0_7=20
    - ct1_0=20
    - ct1_1=20
    - ct1_2=20
    - ct1_3=20
    - ct1_4=20
    - ct1_5=20
    - ct1_6=30
    - ct1_7=20
    devices:
    - /dev/spidev0.0
```

### docker cli ([click here for more info](https://docs.docker.com/engine/reference/commandline/cli/))

```bash
docker run -d \
  --name=energymeter \
  --device=/dev/spidev0.0 \
  -e ct0_0=100 \
  -e ct0_1=100 \
  -e ct0_2=30 \
  -e ct0_3=30 \
  -e ct0_4=20 \
  -e ct0_5=20 \
  -e ct0_6=20 \
  -e ct0_7=20 \
  -e ct1_0=20 \
  -e ct1_1=20 \
  -e ct1_2=20 \
  -e ct1_3=20 \
  -e ct1_4=20 \
  -e ct1_5=20 \
  -e ct1_6=30 \
  -e ct1_7=20 \
  --restart always \
  slothcroissant/rpi-energymeter:nightly
```

## Environment Variables

When running the `docker run` command, the Docker CLI client checks the value the variable has in your local environment and passes it to the container. If no `=` is provided and that variable is not exported in your local environment, the variable won’t be set in the container.

| Env Var | Function |
| ---- | --- |
| `-e ctX=YY` | Set the amperage rating YY for ct X. You can find this directly on the CT clamp itself if needed |

## Consuming Data

Once running, the application listens at `0.0.0.0.:5000`, and can be easily accessed and queried at `http://<ip_address>:5000/`. For example:

`curl http://energymeter.lan:5000/`

## Limitations / To-Do
   
To-do items can be found in GitHub Issues via the "[Enhancement](https://github.com/SlothCroissant/rpi-energymeter/issues?q=is%3Aissue+label%3Aenhancement)" tag.