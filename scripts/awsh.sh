#!/bin/bash

result=$(awshpy ${@:1})

if [ $? != 2 ]; then
  echo -n $result
  exit
fi

ip=$(echo $result | cut -f1 -d$'~')
key=$(echo $result | cut -f2 -d$'~')

ssh -o "StrictHostKeyChecking no" -i $key ubuntu@$ip
