ABORT_ERROR_MESSAGE="Skipping attempt to load environment variables from secret. Action may fail if environment variables have not been configured."

if [ -x "$(command -v transcrypt)" ]; then
  FILE=./.env.enc
  if [ -f $FILE ]; then
    while read line; do
      export $line
    done < $FILE
  else
    echo "$FILE does not exist. $ABORT_ERROR_MESSAGE"
  fi
else
  echo "Transcrypt is not installed. $ABORT_ERROR_MESSAGE"
fi
