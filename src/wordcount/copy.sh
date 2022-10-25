#!/bin/bash

IPV4_ADDRESS=$(cat ../aws_data.json | python3.9 -mjson.tool | grep -Eo '([[:digit:]]{1,3}\.[[:digit:]]{1,3}\.[[:digit:]]{1,3}\.[[:digit:]]{1,3})')

sudo scp -i ../ec2_keypair.pem WordCount.java ubuntu@"$IPV4_ADDRESS":/home/ubuntu
sudo scp -i ../ec2_keypair.pem setup.sh ubuntu@"$IPV4_ADDRESS":/home/ubuntu