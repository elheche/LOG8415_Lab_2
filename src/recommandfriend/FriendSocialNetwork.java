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
        //System.out.println("couple :("+ friendOne + "," + friendTwo + "_" + zero.toString() +")");
        context.write(friendOne, new Text(friendTwo + "_" + zero));
        mutualFriends.add(friendTwo.toString());
      }

      for (int i=0; i < mutualFriends.size(); i++){
        for (int j=i+1; j < mutualFriends.size(); j++){
            context.write(new Text(mutualFriends.get(i)), new Text(mutualFriends.get(j) + "_" + one));
            context.write(new Text(mutualFriends.get(j)), new Text(mutualFriends.get(i) + "_" + one));
            //System.out.println("couple :("+ mutualFriends.get(i) + "," + mutualFriends.get(j) + "_" + one.toString() +")");
            //System.out.println("couple :("+ mutualFriends.get(j) + "," + mutualFriends.get(i) + "_" + one.toString() +")");
        }
      }
    }
  }

  public static class SumReducer
       extends Reducer<Text,Text,Text,Text> {
    private Text result = new Text();

    public void reduce(Text key, Iterable<Text> values,
                       Context context
                       ) throws IOException, InterruptedException {

      Hashtable<String, Integer> mutualFriendsDict = new Hashtable<String, Integer>();
      for (Text val : values) {
        String[] elements = val.toString().split("_");
        //System.out.println("the input value is " + val.toString() + "|");
        if (elements.length > 1){
            //System.out.println(elements[0]);
            //System.out.println(elements[1]);
            String friendTwo = elements[0];
            int relationship = Integer.parseInt(elements[1]);
            if (mutualFriendsDict.containsKey(friendTwo)){
                int count = mutualFriendsDict.get(friendTwo);
                if (relationship == 0){
                    mutualFriendsDict.put(friendTwo, 0);
                }
                else if ((relationship == 1) && (count != 0)) {
                    mutualFriendsDict.put(friendTwo, count + 1);
                }
            } else {
                mutualFriendsDict.put(friendTwo, relationship);
            }
        }
      }

     /*Set<Map.Entry<String, Integer>> entries = mutualFriendsDict.entrySet();
      for(Map.Entry<String, Integer> entry : entries ){
        System.out.println( entry.getKey() + "->" + entry.getValue() );
      }*/

      //get all the entries from the hashtable and put it in a List
      List<Map.Entry<String, Integer>> list = new ArrayList<Entry<String, Integer>>(mutualFriendsDict.entrySet());
      //sort the entries based on the value by custom Comparator
      Collections.sort(list, new Comparator<Map.Entry<String, Integer>>(){
        public int compare(Entry<String, Integer> entry2, Entry<String, Integer> entry1) {
            return entry1.getValue().compareTo( entry2.getValue());
        }
      });

      /*for(Map.Entry<String, Integer> entry : list){
        System.out.println( entry.getKey() + "->" + entry.getValue() );
      }*/

      String output = "\t";
      for( Map.Entry<String, Integer> entry : list){
        if (entry.getValue() != 0){
            //output = output + entry.getKey() + "(" + entry.getValue().toString() + "),";
            output = output + entry.getKey() + ",";
        } else {
            break;
        }
      }

      output = output.substring(0, output.length() - 1);
      //System.out.println("the result is " + output + "|");
      result = new Text(output);
      context.write(key, result);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "friend social network");
    job.setJarByClass(FriendSocialNetwork.class);
    job.setMapperClass(GraphMapper.class);
    //job.setCombinerClass(SumReducer.class);
    job.setReducerClass(SumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }

}