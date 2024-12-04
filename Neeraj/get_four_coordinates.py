import math

def main():
    v = []

    for i in range(-89, 88):
        j = -179
        while j < 178:
            # Append the coordinates to the vector
            v.append((i, j))
            v.append((i + 1, j))

            # Convert latitude to radians
            latitude = math.radians(i)
            
            # Calculate new longitude values based on the latitude
            v.append((i, j + (1 / math.cos(latitude))))
            v.append((i + 1, j + (1 / math.cos(latitude + math.radians(1)))))
            
            # Update j for the next iteration
            j += (1 / math.cos(latitude))

    return v

if __name__ == "__main__":
    v = main()
    # print(v)
