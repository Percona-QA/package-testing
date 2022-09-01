#!/usr/bin/env bash
# use this if running initial setup directly from server which is being setup
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt-get update
sudo apt-get install -y ansible
