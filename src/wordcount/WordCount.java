import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
* Class defining the word count of each word in a file using the MapReduce Paradigm.
* This class define the both Mapper and Reducer class necessary for the word count task.
* <p>
*/

public class WordCount {
  /**
  * Class defining the Mapper class necessary for the word count task.
  * this class override the class Mapper from org.apache.hadoop.mapreduce
  * and return a couple (Text, IntWritable)
  * <p>
  */
  public static class TokenizerMapper
       extends Mapper<Object, Text, Text, IntWritable>{

    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();

    /**
    * this method implement the logic of the mapping step of MapReduce paradigm
    * <p>
    *
    * @param  key  the input key.
    * @param  value the input key.
    * @param  context the object to interact with the rest of the Hadoop system.
    * @return       collects mapped keys and values.
    */
    public void map(Object key, Text value, Context context
                    ) throws IOException, InterruptedException {
      StringTokenizer itr = new StringTokenizer(value.toString());
      while (itr.hasMoreTokens()) {
        word.set(itr.nextToken());
        context.write(word, one);
      }
    }
  }

  /**
  * Class defining the Reducer class necessary for the word count task.
  * this class override the class Reducer from org.apache.hadoop.mapreduce
  * and return a couple (Text, IntWritable)
  * <p>
  */
  public static class IntSumReducer
       extends Reducer<Text,IntWritable,Text,IntWritable> {
    private IntWritable result = new IntWritable();
    /**
    * this method implement the logic of the reducing (merging) step of MapReduce paradigm
    * <p>
    *
    * @param  key  the input key (taken from map output).
    * @param  value the input key (taken from map output).
    * @param  context the object to interact with the rest of the Hadoop system.
    * @return       collects mapped keys and values.
    */
    public void reduce(Text key, Iterable<IntWritable> values,
                       Context context
                       ) throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable val : values) {
        sum += val.get();
      }
      result.set(sum);
      context.write(key, result);
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
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}