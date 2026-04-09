from pyspark.sql import SparkSession

# Create Spark session in LOCAL mode (no Docker needed!)
spark = SparkSession.builder \
    .appName('Test Spark Local') \
    .master('local[*]') \
    .getOrCreate()

print('✅ Spark Version:', spark.version)
print('✅ Spark running in LOCAL mode')

# Create a simple DataFrame
data = [
    ('India', 'Electronics', 1000000),
    ('USA', 'Machinery', 2000000),
    ('China', 'Textiles', 1500000)
]

df = spark.createDataFrame(data, ['country', 'product', 'trade_value'])

print('\n✅ Sample Trade Data:')
df.show()

print('\n✅ Trade by Country:')
df.groupBy('country').sum('trade_value').show()

spark.stop()
print('\n✅ PySpark test completed successfully!')
