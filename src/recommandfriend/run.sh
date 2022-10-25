#!/bin/bash
echo "Creating input directory..."
hdfs dfs -mkdir input
echo "Done."
echo "Copying datasets from to input directory..."
hdfs dfs -copyFromLocal soc-LiveJournal1Adj.txt input
echo "Done."
echo "delete output if exist directory..."
hdfs dfs -rm -r output
echo "Done."
echo "Running friend recommendation on Hadoop..."
hadoop jar friends.jar org.myorg.Friends input output
echo "Done."
echo "Getting output...."
hdfs dfs -copyToLocal -f output
echo "Done."