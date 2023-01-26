Platypus
========
[![Build Status](https://travis-ci.com/MyNameIsMikeGreen/platypus.svg?branch=master)](https://travis-ci.com/MyNameIsMikeGreen/platypus)

Django web server providing Mike Green's recipes.

> **Note**
> This project is no longer publicly hosted

# Usage (Local)

## Pre-Requisites

### Utilities
* [Docker](https://www.docker.com/)

## Test

Local testing steps are identical to the [production testing steps](#usage-production).

## Launch

Launch the application and associated database using Docker:

```bash
docker-compose up
```

# Usage (Production)

## Pre-Requisites

### Utilities
* [Python 3.8+](https://www.python.org/)

### Database Setup

Platypus requires an SQLite instance to store recipe data. A simple fresh instance with some database and user is sufficient to start with.

Run the following to (re)initialise the database referenced in the environment variables:

```bash
./reset-database.sh
```

This will destroy any existing database, run all migrations, and populate it with data.

## Test

Run all tests:

```bash
./test.sh
```

## Launch

Launch the server:

```bash
./run.sh
```

# Contributing
If you wish to contribute to Platypus, please see the [Contributing Guidelines](CONTRIBUTING.md).
