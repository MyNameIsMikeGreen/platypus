FROM python:3.9-alpine3.18

WORKDIR /usr/src/app
COPY . .

## Convert line endings to Linux-style if not already
#RUN apk add --update curl  \
#    && curl https://github.com/mdolidon/endlines/raw/master/download/endlines-1.9.2-linux-amd64 --output ./endlines  \
#    && chmod +x ./endlines  \
#    && ./endlines linux -r *

# Install dependencies
RUN apk add --no-cache postgresql-libs  \
    && apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev  \
    && pip install --no-cache-dir -r requirements.txt  \
    && apk --purge del .build-deps

# Run app
EXPOSE 8000
CMD [ "./run.sh" ]
