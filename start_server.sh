#!/bin/bash

echo "starting server..."
python server.py > ../tornado.log 2>&1 &
echo $! > ../tornado.pid
disown
