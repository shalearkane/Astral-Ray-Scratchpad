import os
from .constants.misc import *

# Create pipe if it doesn't exist
if not os.path.exists(STATISTICS_COMM_PIPE):
    os.mkfifo(STATISTICS_COMM_PIPE)

count_0 = 0
count_1 = 0

try:
    while True:
        # Open pipe in read mode
        with open(PIPE_PATH, "r") as pipe:
            for number in pipe:
                number = number.strip()
                if number == "0":
                    count_0 += 1
                elif number == "1":
                    count_1 += 1
                print(f"Current counts - 0s: {count_0}, 1s: {count_1}")
except KeyboardInterrupt:
    print("\nStopping reader...")
finally:
    if os.path.exists(PIPE_PATH):
        os.remove(PIPE_PATH)
