#!/usr/bin/env bash
gunicorn -w 3 main:app
