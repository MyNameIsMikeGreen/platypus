FILE=./.env.enc
if [ -f $FILE ]; then
  while read line; do
    export $line
  done < $FILE
else
  echo "$FILE does not exist. Action may fail if environment variables have not been configured."
fi
