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

  public static class IntSumReducer
       extends Reducer<Text,Text,Text,Text> {
    private Text result = new Text();

    public void reduce(Text key, Iterable<Text> values,
                       Context context
                       ) throws IOException, InterruptedException {
      /*int sum = 0;
      for (Text val : values) {
        sum += val.get();
      }
      result.set(sum);*/
      context.write(key, new Text("Test"));
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "word count");
    job.setJarByClass(WordCount.class);
    job.setMapperClass(TokenizerMapper.class);
    job.setCombinerClass(IntSumReducer.class);
    job.setReducerClass(IntSumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }

}