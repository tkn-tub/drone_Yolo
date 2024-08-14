import pandas as pd

# Load the data from CSV
df = pd.read_csv('average_latencies_bot.csv')

# Calculate the individual average latencies
average_preprocessing_latency = df['Average Preprocessing Latency (ms)'].mean()
average_inference_latency = df['Average Inference Latency (ms)'].mean()
average_postprocessing_latency = df['Average Postprocessing Latency (ms)'].mean()
average_total_latency = df['Average Total Latency (ms)'].mean()

print(f'Average Preprocessing Latency (ms): {average_preprocessing_latency}')
print(f'Average Inference Latency (ms): {average_inference_latency}')
print(f'Average Postprocessing Latency (ms): {average_postprocessing_latency}')
print(f'Average Total Latency (ms): {average_total_latency}')
