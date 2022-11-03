#!/bin/bash

update_package_list() {
    if ! sudo apt-get -o DPkg::Lock::Timeout=60 update -y &>/dev/null; then
        echo "Failed to update package list, please try again."
        retrun 1
    fi
}

install_dependencies() {
    if ! sudo apt-get -o DPkg::Lock::Timeout=60 install default-jdk -y &>/dev/null; then
        echo "Failed to install dependencies, please try again."
        retrun 1
    fi
}

echo "Updating package list..."
update_package_list
echo "Done."

echo "Installing dependencies..."
install_dependencies
echo "Done."

echo "Setting environment variables for java, hadoop and spark..."
echo "export JAVA_HOME=/usr/lib/jvm/default-java" | sudo tee -a .profile >/dev/null
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" | sudo tee -a .profile >/dev/null
echo "export SPARK_HOME=/usr/local/spark-2.0.0-bin-hadoop2.7" | sudo tee -a .profile >/dev/null
echo "export PATH=\$PATH:\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$SPARK_HOME/bin" | sudo tee -a .profile >/dev/null
source .profile
echo "Done."

echo "Downloading Hadoop-3.3.4..."
sudo curl -O https://dlcdn.apache.org/hadoop/common/stable/hadoop-3.3.4.tar.gz 2>/dev/null
echo "Done."

echo "Downloading Spark-2.0.0..."
sudo curl -O https://archive.apache.org/dist/spark/spark-2.0.0/spark-2.0.0-bin-hadoop2.7.tgz 2>/dev/null
echo "Done."

echo "Installing Hadoop-3.3.4..."
sudo tar -xf hadoop-3.3.4.tar.gz -C /usr/local/
echo "Done."

echo "Installing Spark-2.0.0..."
sudo tar -xf spark-2.0.0-bin-hadoop2.7.tgz -C /usr/local/
echo "Done."

echo "Setting specific environment variables for hadoop..."
echo "export JAVA_HOME=/usr/lib/jvm/default-java" | sudo tee -a /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh >/dev/null
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" | sudo tee -a /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh >/dev/null
echo "Done."

echo "Compiling WordCount.java..."
hadoop com.sun.tools.javac.Main WordCount.java
sudo jar cf wc.jar WordCount*.class
echo "Done."

echo "Creating input directory..."
hdfs dfs -mkdir input
echo "Done."

echo "Creating data directory..."
mkdir data
echo "Done."

echo "Downloading datasets..."
sudo curl -L --compressed http://www.gutenberg.org/cache/epub/4300/pg4300.txt -o data/pg4300.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/buchanj-midwinter/buchanj-midwinter-00-t.txt -o data/buchanj-midwinter-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/carman-farhorizons/carman-farhorizons-00-t.txt -o data/carman-farhorizons-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/colby-champlain/colby-champlain-00-t.txt -o data/colby-champlain-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/cheyneyp-darkbahama/cheyneyp-darkbahama-00-t.txt -o data/cheyneyp-darkbahama-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/delamare-bumps/delamare-bumps-00-t.txt -o data/delamare-bumps-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/charlesworth-scene/charlesworth-scene-00-t.txt -o data/charlesworth-scene-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/delamare-lucy/delamare-lucy-00-t.txt -o data/delamare-lucy-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/delamare-myfanwy/delamare-myfanwy-00-t.txt -o data/delamare-myfanwy-00-t.txt 2>/dev/null
sudo curl -L --compressed http://www.gutenberg.ca/ebooks/delamare-penny/delamare-penny-00-t.txt -o data/delamare-penny-00-t.txt 2>/dev/null
echo "Done."

echo "Moving friend social network dataset to data directory..."
mv soc-LiveJournal1Adj.txt data
echo "Done."

echo "Copying datasets from data to input directory..."
hdfs dfs -copyFromLocal data/* input
echo "Done."

echo "Creating time.txt file..."
touch time.txt
echo "Done."

echo "Running WordCount on Hadoop vs Linux..."
printf "############################################\n" | sudo tee -a time.txt >/dev/null
printf "WordCount execution time on Hadoop vs Linux\n" | sudo tee -a time.txt >/dev/null
printf "############################################\n" | sudo tee -a time.txt >/dev/null
printf -- "--------------------------------------------\n" | sudo tee -a time.txt >/dev/null
printf "Hadoop:\n" | sudo tee -a time.txt >/dev/null
printf -- "--------------------------------------------" | sudo tee -a time.txt >/dev/null
(time (hadoop jar wc.jar WordCount ./input/pg4300.txt output &>/dev/null)) &>>time.txt
printf -- "--------------------------------------------\n" | sudo tee -a time.txt >/dev/null
printf "Linux:\n" | sudo tee -a time.txt >/dev/null
printf -- "--------------------------------------------" | sudo tee -a time.txt >/dev/null
(time (tr <./input/pg4300.txt -c "[:graph:]" "\n" | sort | uniq -c &>/dev/null)) &>>time.txt
echo "Done."

echo "Running WordCount on Hadoop..."
printf "############################################\n" | sudo tee -a time.txt >/dev/null
printf "WordCount execution time on Hadoop\n" | sudo tee -a time.txt >/dev/null
printf "############################################\n" | sudo tee -a time.txt >/dev/null
for ((i = 1; i <= 3; i++)); do
    echo "Running test #$i..."
    printf -- "*******************\n" | sudo tee -a time.txt >/dev/null
    printf "Test: #%s\n" "$i" | sudo tee -a time.txt >/dev/null
    printf -- "*******************\n" | sudo tee -a time.txt >/dev/null
    for dataset in ./input/*.txt; do
        if [[ "$dataset" == "./input/pg4300.txt" || "$dataset" == "./input/soc-LiveJournal1Adj.txt" ]]; then
            continue
        fi
        hdfs dfs -rm -r output &>/dev/null
        printf -- "--------------------------------------------\n" | sudo tee -a time.txt >/dev/null
        printf "Dataset: %s\n" "$dataset" | sudo tee -a time.txt >/dev/null
        printf -- "--------------------------------------------" | sudo tee -a time.txt >/dev/null
        (time (hadoop jar wc.jar WordCount "$dataset" output &>/dev/null)) &>>time.txt
    done
done
echo "Done."

echo "Running WordCount on Spark..."
printf "############################################\n" | sudo tee -a time.txt >/dev/null
printf "WordCount execution time on Spark\n" | sudo tee -a time.txt >/dev/null
printf "############################################\n" | sudo tee -a time.txt >/dev/null
for ((i = 1; i <= 3; i++)); do
    echo "Running test #$i..."
    printf -- "*******************\n" | sudo tee -a time.txt >/dev/null
    printf "Test: #%s\n" "$i" | sudo tee -a time.txt >/dev/null
    printf -- "*******************\n" | sudo tee -a time.txt >/dev/null
    for dataset in ./input/*.txt; do
        if [[ "$dataset" == "./input/pg4300.txt" || "$dataset" == "./input/soc-LiveJournal1Adj.txt" ]]; then
            continue
        fi
        hdfs dfs -rm -r output &>/dev/null
        printf -- "--------------------------------------------\n" | sudo tee -a time.txt >/dev/null
        printf "Dataset: %s\n" "$dataset" | sudo tee -a time.txt >/dev/null
        printf -- "--------------------------------------------" | sudo tee -a time.txt >/dev/null
        (time (spark-submit --class WordCount wc.jar "$dataset" output &>/dev/null)) &>>time.txt
    done
done
echo "Done."

echo "Execution time successfully saved in time.txt"

echo "Compiling FriendSocialNetwork.java..."
hadoop com.sun.tools.javac.Main FriendSocialNetwork.java
sudo jar cf fsn.jar FriendSocialNetwork*.class
echo "Done."

echo "Running FriendSocialNetwork on Hadoop..."
hdfs dfs -rm -r output &>/dev/null
hadoop jar fsn.jar FriendSocialNetwork ./input/soc-LiveJournal1Adj.txt output &>/dev/null
echo "Done."

echo "Creating mutual_friend.txt file..."
touch time.txt
echo "Done."

echo "Saving list of mutual friend for ids: 924 8941 8942 9019 9020 9021 9022 9990 9992 9993..."
array=(924 8941 8942 9019 9020 9021 9022 9990 9992 9993)
for i in "${array[@]}"; do
    grep <./output/part-r-00000 ^"$i"$'\t' >>mutual_friend.txt
done
echo "Done"
