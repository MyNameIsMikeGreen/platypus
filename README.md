Platypus
========

Django web server providing Mike Green's recipes.

Hosted on Heroku: https://mike-green-platypus.herokuapp.com/

# Usage

## Pre-Requisites

### Environment Variables

The following environment variable must be set before running

* `DB_HOST`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`

### Database Migrations

Ensure the database is up-to-date before launching by running the migrations:

```bash
./migrate.sh
```

## Launch

Launch the server:

```bash
./run.sh
```

