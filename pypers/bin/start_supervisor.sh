#!/bin/bash

usage() {
  echo "Usage: $0 [env cfg]"
  echo "where <env> is the path to the virtual environment"
  echo "      <cfg> is the path to the supervisord configuration file"
}

if [[ $1 =~ -{1,2}h ]]; then
 usage
 exit 0
fi

config="supervisord.conf"

wherami=`hostname`
export ACME_LCL=1
venv_dir=$1
config=$2
echo "Activating environment from $venv_dir"
source activate $venv_dir

echo -n "Killing existing supervisord process (if any)..."
pkill -9 gunicorn
echo -n "."
sleep 1
killall supervisord
if [ $? -eq 0 ]; then
  while [[ "`/sbin/pidof -s -x supervisord`" -ne 0 ]]; do
    echo -n "."
    sleep 1
  done
  echo "Successfully killed supervisord"
else
  echo
  echo "Couldn't kill supervisord ==> assuming it's not running"
fi

echo "Starting supervisor daemon with $config... "
supervisord -c $config || exit $?

echo "Done."
echo
echo "==> Check it out at http://"`hostname`":9001 <=="
