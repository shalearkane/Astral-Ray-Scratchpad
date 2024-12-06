import os
from constants.misc import STATISTICS_COMM_PIPE

# Create pipe if it doesn't exist
if not os.path.exists(STATISTICS_COMM_PIPE):
    os.mkfifo(STATISTICS_COMM_PIPE)

count_0 = 0
count_1 = 0

try:
    while True:
        # Open pipe in read mode
        with open(STATISTICS_COMM_PIPE, "r") as pipe, open("output.csv", "a") as out:
            for line in pipe:
                out.write(line)
                print(f"{line}")
except KeyboardInterrupt:
    print("\nStopping reader...")
finally:
    if os.path.exists(STATISTICS_COMM_PIPE):
        os.remove(STATISTICS_COMM_PIPE)
