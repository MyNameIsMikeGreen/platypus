Platypus
========
[![Build Status](https://travis-ci.com/MyNameIsMikeGreen/platypus.svg?branch=master)](https://travis-ci.com/MyNameIsMikeGreen/platypus)

Django web server providing Mike Green's recipes.

Hosted on Heroku:
* https://MyNameIsMikeGreen.co.uk/
* https://mike-green-platypus.herokuapp.com/

# Usage (Local)

## Pre-Requisites

### Utilities
* Docker

## Test

Local testing steps are identical to the [production testing steps](#usage-production)

## Launch

Launch the server using Docker:

```bash
./run.sh
```

# Usage (Production)

## Pre-Requisites

### Utilities
* Python 3.8+
* Pip
* (Optional) Transcrypt

### Environment Variables

Platypus requires several environment variables to be set before any interaction with the system can be carried out (including testing). These can either be set manually using standard IDE or OS methods, or the values can be automatically decrypted and utilised using [Transcrypt](https://github.com/elasticdog/transcrypt).

#### Manual

The following environment variable must be set before running

* `DB_HOST`: Host URL of database.
* `DB_NAME`: Name of database.
* `DB_USER`: User with read access in the database.
* `DB_PASSWORD`: Password of the database user.
* `SECRET_KEY`: Cryptographic key for signing.
* `DEBUG`: Enables or disables debug mode. Application will return HTTP 500 to all requests if deployed with debug mode enabled.

#### Transcrypt

To use Transcrypt, you must know the password. If you don't, give up and use the manual approach above.

* Install [Transcrypt](https://github.com/elasticdog/transcrypt) according to the [official documentation](https://github.com/elasticdog/transcrypt/blob/main/INSTALL.md).
* Initialise the repository:
  ```
  transcrypt -c aes-256-cbc -p '[PASSWORD]'
  ```

### Database Setup

Platypus requires a PostgreSQL instance to store recipe data. A simple fresh instance with some database and user is sufficient to start with.

Run the following to (re)initialise the PostgreSQL database referenced in the environment variables:

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