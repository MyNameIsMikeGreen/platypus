Platypus
========
[![Build Status](https://travis-ci.com/MyNameIsMikeGreen/platypus.svg?branch=master)](https://travis-ci.com/MyNameIsMikeGreen/platypus)

Django web server providing Mike Green's recipes.

Hosted on Heroku: https://mike-green-platypus.herokuapp.com/

# Usage

## Pre-Requisites

### Utilities
* Python 3.6+
* Pip
* (Optional) Transcrypt

### Environment Variables

Platypus requires several environment variables to be set before any interaction with the system can be carried out (including testing). These can either be set manually using standard IDE or OS methods, or the values can be automatically decrypted and utilised using [Transcrypt](https://github.com/elasticdog/transcrypt).

#### Manual

The following environment variables must be set before running

Create setup.sh in the root folder

    touch setup.sh

and update it with appropriate variables:

      export DB_HOST=""
      export DB_PORT=""
      export DB_NAME=""
      export DB_USER=""
      export DB_PASSWORD=""
      export SECRET_KEY=""
      export DEBUG=""
      # Enables or disables debug mode. Application will return HTTP 500
      # to all requests if deployed with debug mode enabled.

Start the PostgreSQL server:

    sudo service postgresql start

Create local database:

    sudo -u postgres create_db <db_name>

#### Virtual Environment

Install virtual environment and activate it:

    sudo pip3 install virtualenv

    virtual venv

    source venv/bin/activate


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