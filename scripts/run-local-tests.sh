#!/usr/bin/env bash

HERE=$(cd "$(dirname "$0")"; pwd)
cd $HERE/..

nosetests -v --exe --with-coverage --cover-package tcgen --with-xunit --cover-erase
coverage html
