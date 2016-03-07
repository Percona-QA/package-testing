#!/bin/bash

for i in `cat /vagrant/pt`; do $i --version; done
