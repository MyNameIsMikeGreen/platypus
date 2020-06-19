Platypus
========

Django web server providing Mike Green's recipes.

Hosted on Heroku: https://mike-green-platypus.herokuapp.com/

# Usage

## Pre-Requisites

### Environment Variables

The following environment variable must be set before running

* `DB_HOST`: Host URL of database.
* `DB_NAME`: Name of database.
* `DB_USER`: User with read access in the database.
* `DB_PASSWORD`: Password of the database user.
* `SECRET_KEY`: Cryptographic key for signing.
* `DEBUG`: Enables or disables debug mode. Application will return HTTP 500 to all requests if deployed with debug mode enabled.

### Database Setup

Ensure the database is up-to-date before launching the application:

```bash
./reset-database.sh
```

This will destroy any existing database, run all migrations, and populate it with data.

## Launch

Launch the server:

```bash
./run.sh
```

