#!/bin/bash


case "$1" in 
terminal)
bash  
;;
*)
eval python3.7 /app/main.py "$@"
;;
esac