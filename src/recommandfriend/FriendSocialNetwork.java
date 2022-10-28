import java.io.IOException;
import java.util.*;
import java.util.Map.Entry;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class FriendSocialNetwork {

  /*void generatePermutations(List<List<String>> lists, List<String> result, int depth, String current) {
    if (depth == lists.size()) {
        result.add(current);
        return;
    }

    for (int i = 0; i < lists.get(depth).size(); i++) {
        generatePermutations(lists, result, depth + 1, current + lists.get(depth).get(i));
    }
  }*/

  public static class GraphMapper
       extends Mapper<Object, Text, Text, Text>{

    // one refers to mutual friend relationship
    private Text one = new Text("1");
    // zero refers to friend relationship
    private Text zero = new Text("0");
    private Text friendOne = new Text();
    private Text friendTwo = new Text();

    public void map(Object key, Text value, Context context
                    ) throws IOException, InterruptedException {
      List<String> mutualFriends = new ArrayList<>();
      StringTokenizer itr = new StringTokenizer(value.toString().replaceAll("\t", ","), ",");
      friendOne.set(itr.nextToken());
      while (itr.hasMoreTokens()) {
        friendTwo.set(itr.nextToken());
        System.out.println("couple :("+ friendOne + "," + friendTwo + "_" + zero.toString() +")");
        context.write(friendOne, new Text(friendTwo + "_" + zero));
        mutualFriends.add(friendTwo.toString());
      }

      for (int i=0; i < mutualFriends.size(); i++){
        for (int j=i+1; j < mutualFriends.size(); j++){
            context.write(new Text(mutualFriends.get(i)), new Text(mutualFriends.get(j) + "_" + one));
            context.write(new Text(mutualFriends.get(j)), new Text(mutualFriends.get(i) + "_" + one));
            System.out.println("couple :("+ mutualFriends.get(i) + "," + mutualFriends.get(j) + "_" + one.toString() +")");
            System.out.println("couple :("+ mutualFriends.get(j) + "," + mutualFriends.get(i) + "_" + one.toString() +")");
        }
      }
    }
  }

}