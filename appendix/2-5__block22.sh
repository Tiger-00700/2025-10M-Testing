spark-submit \
  --conf spark.metrics.conf=<path>/metrics.properties \
  --conf spark.metrics.namespace=my-spark-app \
  --class com.example.MySparkApp \
  my-spark-app.jar
