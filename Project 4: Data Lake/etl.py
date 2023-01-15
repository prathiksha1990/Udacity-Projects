import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import week,year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql.types import StructType as R, StructField as Fld, DoubleType as Dbl, \
                                StringType as Str, IntegerType as Int, DateType as Dat, \
                                TimestampType
from pyspark.sql.functions import to_timestamp as ti

config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    This function loads song_data from S3, extracts songs and artist data and loads it back to S3 
    
    Parameters:
     spark      : Spark Session
     input_data : location of song_data json files including song/user metadata
     output_data: S3 bucket
    
    """
    # get filepath to song data file
    song_data = input_data + 'song_data/*/*/*/*.json'
    
     #define the song schema
    songSchema = R([
        Fld("artist_id",Str()),
        Fld("artist_latitude",Dbl()),
        Fld("artist_location",Str()),
        Fld("artist_longitude",Dbl()),
        Fld("artist_name",Str()),
        Fld("duration",Dbl()),
        Fld("num_songs",Int()),
        Fld("song_id",Str()),
        Fld("title",Str()),
        Fld("year",Int()),
    ])
    
    # read song data file
    df = spark.read.json(song_data, schema=songSchema)

    # extract columns to create songs table
    songs_columns = ["song_id","title", "artist_id","year","duration"]
    songs_table = df.select(song_columns).dropDuplicates(["song_id"])
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy("year","artist_id").parquet(output_data + 'songs/')

    # extract columns to create artists table
    artists_columns = ["artist_id", "artist_name as name", "artist_location as location",\
                       "artist_latitude as latitude", "artist_longitude as longitude"]
    artists_table = df.selectExpr(artists_columns).dropDuplicates(["artist_id"])
    
    # write artists table to parquet files
    artists_table.write.parquet(output_data + 'artists/')


def process_log_data(spark, input_data, output_data):
    """
       This functions loads log_data from S3 and processes it byextracting the users, time and              songplays tables and laods it back to S3 
       
       Parameters:
         spark      : Spark session
         input_data : location of log_data json files with log data
         output_data: S3 bucket where data is stored parquet format
         
    """
    # get filepath to log data file
    log_data = input_data + 'log_data/*/*/*.json'

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong')

    # extract columns for users table  
    user_columns = ["userId", "firstName","lastName","gender","level"]
    user_table = df.selectExpr(user_columns).dropDuplicates(["userId"])
    
    # write users table to parquet files
    user_table.write.parquet(output_data + 'users/')

    # create timestamp column from original timestamp column
    df = df.withColumn("start_time", (col("ts")/1000).cast("timestamp"))
    
    # extract columns to create time table

    time_table = df.select("start_time").dropDuplicates(["start_time"]) \
            .withColumn("hour", hour(col("start_time"))) \
            .withColumn("day", date_format(col("start_time"), "d")) \
            .withColumn("week", weekofyear(col("start_time"))) \
            .withColumn("month", month(col("start_time"))) \
            .withColumn("year", year(col("start_time"))) \
            .withColumn("weekday", date_format(col("start_time"), 'E'))
    
    # write time table to parquet files partitioned by year and month
    time_table.write.partitionBy("year","month").parquet(output_data + 'time/')

    # read in song data to use for songplays table
    song_df    = spark.read.parquet(output_data + 'songs/*/*/*')
    artists_df = spark.read.parquet(output_data + 'artists/*')
    
    songs_logs = df.join(song_df, (df.song == song_df.title))
    artists_songs_logs = songs_logs.join(artists_df,(songs_logs.artist == artists_df.name)) \
    .drop(artists_df.location)

    # extract columns from joined song and log datasets to create songplays table 
    songplays = artists_songs_logs.join(time_table, \
    artists_songs_logs.start_time == time_table.start_time, 'left' \
    ).drop(artists_songs_logs.start_time)

   
    songplays_table = songplays.select(
     col('start_time').alias('start_time'),
     col('userId'.alias('user_id'),
     col('level').alias('level'),
     col('artist_id').alias('artist_id'),
     col('sessionId').alias('session_id'),
     col('location').alias('location'),
     col('userAgent').alias('user_agent'),
     col('year').alias('year'),
     col('month').alias('month'),
        ).repartition("year","month")
        
    # write songplays table to parquet files partitioned by year and month
        
    songplays_table.write.partitionBy("year","month").parquet(output_data + 'songplays/')


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = ""
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
