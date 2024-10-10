import pandas as pd
from datetime import datetime, timedelta

# Function to convert time strings
def parse_time_string(time_str):
    if pd.isna(time_str) or time_str.strip() == "":
        return timedelta(0)  # If the string is empty or NaN, return 0 timedelta
    try:
        # Remove non-time characters and extra spaces
        time_str = time_str.strip().replace('i', '').replace('o', '').replace('OWN', '').strip()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        return timedelta(hours=time_obj.hour, minutes=time_obj.minute)
    except ValueError:
        return timedelta(0)

threshold_hours = float(input("Enter the weekly threshold in hours (e.g., 30): "))

file_path = input("Enter the CSV file name (with path if not in the current directory): ")

# Read the CSV file
try:
    df = pd.read_csv(file_path, header=None, encoding='utf-8') # No header assumed
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check the file name and try again.")
    exit()

df.columns = ['Date', 'Weekday', 'SomeColumn', 'AnotherColumn', 'Time1', 'Time2', 'Time3', 'Time4', 'Empty1', 'Empty2', 'DailyCumulative', 'WeeklyCumulative']

df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%y', errors='coerce')

df['Time1'] = df['Time1'].apply(parse_time_string)
df['Time2'] = df['Time2'].apply(parse_time_string)
df['Time3'] = df['Time3'].apply(parse_time_string)
df['Time4'] = df['Time4'].apply(parse_time_string)

# Calculate total daily hours worked
df['DailyHoursWorked'] = (df['Time2'] - df['Time1'] + df['Time4'] - df['Time3']).apply(lambda x: x.total_seconds() / 3600)

df = df.dropna(subset=['Date'])

# Ensure correct calculation of the week starting on Monday ("Mo" - "Su")
df['Week Start'] = df['Date'].apply(lambda x: x - timedelta(days=x.weekday()))

# Calculate total hours per week
weekly_hours = df.groupby('Week Start')['DailyHoursWorked'].sum().reset_index()

# Calculate exceeded hours
weekly_hours['Exceeded Hours'] = weekly_hours['DailyHoursWorked'] - threshold_hours
weekly_hours['Exceeded Hours'] = weekly_hours['Exceeded Hours'].apply(lambda x: x if x > 0 else 0)

# Calculate total exceeded hours for the entire time frame
total_exceeded_hours = weekly_hours['Exceeded Hours'].sum()

# Results
print("\nWeekly exceeded hours:")
print(weekly_hours[['Week Start', 'Exceeded Hours']])

print(f"\nTotal exceeded hours for the given time frame: {total_exceeded_hours:.2f}")
