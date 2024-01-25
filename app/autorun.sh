#!/bin/bash


case "$1" in 
    terminal)
        bash  
    ;;
    
    *)
        eval python3.7 /app/main.py "$@"
        cmd_exit="$?"
        if [ "$cmd_exit" -ne 0 ]; then
            exit "$cmd_exit"
        fi
    ;;
esac