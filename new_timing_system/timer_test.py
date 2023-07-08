from datetime import datetime

# get current time
now = datetime.now()

# format time as HH:MM:SS
time_str = now.strftime('%H:%M:%S')

# add fractional seconds
fractional_seconds = str(now.microsecond // 1000).zfill(3)

# construct final timestamp
timestamp = f"{time_str}'{fractional_seconds}\""

print(timestamp)
