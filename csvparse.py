import pandas as pd
from datetime import datetime, timedelta

# Function to convert time strings like "08:00s" into timedelta objects
def parse_time_string(time_str):
    if pd.isna(time_str) or time_str.strip() == "":
        return timedelta(0)  # If the string is empty or NaN, return 0 timedelta
    try:
        # Remove non-time characters and extra spaces
        time_str = time_str.strip().replace('s', '').replace('u', '').replace('OAS', '').strip()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        return timedelta(hours=time_obj.hour, minutes=time_obj.minute)
    except ValueError:
        return timedelta(0)

# Prompt user for the threshold
threshold_hours = float(input("Enter the weekly threshold in hours (e.g., 30): "))

# Prompt user for the CSV file name
file_path = input("Enter the CSV file name (with path if not in the current directory): ")

# Read the CSV file
try:
    df = pd.read_csv(file_path, header=None, encoding='utf-8')  # Assuming the file does not have a header
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check the file name and try again.")
    exit()

# Define columns based on provided data structure
df.columns = ['Date', 'Weekday', 'SomeColumn', 'AnotherColumn', 'Time1', 'Time2', 'Time3', 'Time4', 'Empty1', 'Empty2', 'DailyCumulative', 'WeeklyCumulative']

# Convert the 'Date' column to datetime objects
df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%y', errors='coerce')

# Convert time columns to timedelta
df['Time1'] = df['Time1'].apply(parse_time_string)
df['Time2'] = df['Time2'].apply(parse_time_string)
df['Time3'] = df['Time3'].apply(parse_time_string)
df['Time4'] = df['Time4'].apply(parse_time_string)

# Calculate total daily hours worked
df['DailyHoursWorked'] = (df['Time2'] - df['Time1'] + df['Time4'] - df['Time3']).apply(lambda x: x.total_seconds() / 3600)

# Remove rows with missing dates (e.g., summary rows without date)
df = df.dropna(subset=['Date'])

# Ensure correct calculation of the week starting on Monday ("Ma" - "Su")
df['Week Start'] = df['Date'].apply(lambda x: x - timedelta(days=x.weekday()))

# Calculate total hours per week
weekly_hours = df.groupby('Week Start')['DailyHoursWorked'].sum().reset_index()

# Calculate exceeded hours
weekly_hours['Exceeded Hours'] = weekly_hours['DailyHoursWorked'] - threshold_hours
weekly_hours['Exceeded Hours'] = weekly_hours['Exceeded Hours'].apply(lambda x: x if x > 0 else 0)

# Calculate total exceeded hours for the entire time frame
total_exceeded_hours = weekly_hours['Exceeded Hours'].sum()

# Output results
print("\nWeekly exceeded hours:")
print(weekly_hours[['Week Start', 'Exceeded Hours']])

# Print the total exceeded hours
print(f"\nTotal exceeded hours for the given time frame: {total_exceeded_hours:.2f}")
