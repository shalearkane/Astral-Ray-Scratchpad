from pymongo import MongoClient
from typing import Optional


def convert_coordinates_to_float(
    connection_string: str,
    database_name: str,
    collection_name: str,
    latitude_field: str,
    longitude_field: str,
    new_lat_field: Optional[str] = None,
    new_lng_field: Optional[str] = None,
) -> tuple[int, int]:
    """
    Convert string coordinates to float in MongoDB collection.
    Creates new fields for the float values or updates existing ones.

    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database
        collection_name: Name of the collection
        latitude_field: Field name containing latitude string
        longitude_field: Field name containing longitude string
        new_lat_field: New field name for float latitude (optional)
        new_lng_field: New field name for float longitude (optional)

    Returns:
        tuple containing (number of documents processed, number of documents updated)
    """
    # Use the same field names if new ones aren't specified
    new_lat_field = new_lat_field or f"{latitude_field}_float"
    new_lng_field = new_lng_field or f"{longitude_field}_float"

    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client[database_name]
    collection = db[collection_name]

    # Track statistics
    processed = 0
    updated = 0

    # Process each document
    for doc in collection.find({latitude_field: {"$exists": True}, longitude_field: {"$exists": True}}):
        processed += 1

        try:
            # Convert coordinates to float
            lat_float = float(doc[latitude_field])
            lng_float = float(doc[longitude_field])

            # Update document with new float fields
            result = collection.update_one(
                {"_id": doc["_id"]}, {"$set": {"location": {"type": "Point", "coordinates": [lng_float, lat_float]}}}
            )

            if result.modified_count > 0:
                updated += 1

        except (ValueError, KeyError) as e:
            print(f"Error processing document {doc['_id']}: {str(e)}")
            continue

    client.close()
    return processed, updated


# Example usage
if __name__ == "__main__":
    # Connection details
    MONGO_URI = "mongodb://localhost:27017"
    DB_NAME = "ISRO"
    COLLECTION_NAME = "fibnacci_lat_lon_v2"

    # Convert coordinates
    processed, updated = convert_coordinates_to_float(
        connection_string=MONGO_URI,
        database_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        latitude_field="latitude",
        longitude_field="longitude",
        new_lat_field="lat",
        new_lng_field="lon",
    )

    print(f"Processed {processed} documents")
    print(f"Updated {updated} documents")
