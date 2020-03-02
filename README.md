# rancheros-config-tool

Python script for easier management of big cloud-config.yml files for RancherOS.

## Requirements
Python 3

`pip install ruamel.yaml`

## Usage
1. Add your public keys to a pub_keys file in the same location as pub_keys.template, separated by newline
1. Modify (cloud-config.yml)[./config/cloud-config.yml] to your liking
1. Add all files you want to be put on your server into (system)[./config/system/]
1. Run (build.py)[./build.py].
1. Copy the built-cloud-config.yml into your host or use the provided optional file hosting and set <your-ip>:8080 during RancherOS installation.
