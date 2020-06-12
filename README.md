Heroku Test App
========

# Usage

## Pre-Requisites

### Environment Variables

The following environment variable must be set before running

* `DB_HOST`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`

## Launch

Launch the server using:

```bash
gunicorn main:app
```
