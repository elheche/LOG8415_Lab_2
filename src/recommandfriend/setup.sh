#!/bin/bash

echo "Installing dependencies..."
sudo apt-get update -y >/dev/null
sudo apt-get install default-jdk -y >/dev/null
echo "Done."

echo "Setting environment variables for java and hadoop..."
echo "export JAVA_HOME=/usr/lib/jvm/default-java" | sudo tee -a .profile >/dev/null
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" | sudo tee -a .profile >/dev/null
echo "export PATH=\$PATH:\$JAVA_HOME/bin:\$HADOOP_HOME/bin" | sudo tee -a .profile >/dev/null
source ~/.profile
echo "Done."

echo "Downloading Hadoop-3.3.4..."
sudo curl -O https://dlcdn.apache.org/hadoop/common/stable/hadoop-3.3.4.tar.gz 2>/dev/null
echo "Done."

echo "Installing Hadoop-3.3.4..."
sudo tar -xf hadoop-3.3.4.tar.gz -C /usr/local/
echo "Done."

echo "Setting specific environment variables for hadoop..."
echo "export JAVA_HOME=/usr/lib/jvm/default-java" | sudo tee -a /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh >/dev/null
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" | sudo tee -a /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh >/dev/null
source ~/.profile
echo "Done."

echo "Compiling FriendSocialNetwork.java..."
hadoop com.sun.tools.javac.Main FriendSocialNetwork.java
sudo jar cf fsn.jar FriendSocialNetwork*.class
echo "Done."

echo "Creating input directory..."
hdfs dfs -mkdir input
echo "Done."

echo "Creating data directory..."
mkdir data
cp test.txt data
cp soc-LiveJournal1Adj.txt data
echo "Done."

echo "Copying datasets from data to input directory..."
hdfs dfs -copyFromLocal data/* input
echo "Done."

echo "Running FriendSocialNetwork on Hadoop vs Linux..."
hadoop jar fsn.jar FriendSocialNetwork ./input/test.txt output &>/dev/null
hadoop jar fsn.jar FriendSocialNetwork ./input/soc-LiveJournal1Adj.txt output_2 &>/dev/null
echo "Done."