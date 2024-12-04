from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient("mongodb://172.20.59.218:27017/")
from pymongo import MongoClient

# Connect to MongoDB
db = client["ISRO"]  # Replace with your database name
collection = db["test_fits"]  # Replace with your collection name

# Example usage
fields_to_average_lat = ["v0lat", "v1lat", "v2lat", "v3lat"]  # Replace with your field names
fields_to_average_lon = ["v0lon", "v1lon", "v2lon", "v3lon"]  # Replace with your field names

average_key = "lat"  # Replace with the key where the average will be stored


# Function to calculate the average and update the document
def calculate_and_update_averages():
    # Fetch all documents in the collection
    documents = collection.find().batch_size(10000)

    for document in documents:
        # Extract the values of the specified fields
        values_lat = [document.get(field, 0) for field in fields_to_average_lat]
        avg_value_lat = sum(values_lat) / len(values_lat) if values_lat else 0

        values_lon = [document.get(field, 0) for field in fields_to_average_lon]
        avg_value_lon = sum(values_lon) / len(values_lon) if values_lon else 0

        # Update the document with the new average key
        collection.update_one({"_id": document["_id"]}, {"$set": {"lat": avg_value_lat, "lon": avg_value_lon}})


calculate_and_update_averages()
