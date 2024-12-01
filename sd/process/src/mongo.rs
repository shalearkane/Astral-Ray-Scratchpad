use std::sync::Arc;

use anyhow::{Ok, Result};
use bson::Document;
use mongodb::Client;

const DB: &str = "ISRO";
const COLLECTION: &str = "primary";

pub async fn find_one_and_replace(
    client: Arc<Client>,
    filter: Document,
    doc: Document,
    collection: String,
) -> Result<Option<Document>> {
    let doc = client
        .database(DB)
        .collection::<Document>(collection.as_str())
        .find_one_and_replace(filter, doc)
        .upsert(true)
        .await
        .unwrap();
    Ok(doc)
}

pub async fn find_one(
    client: Arc<Client>,
    collection: String,
    filter: Document,
) -> Result<Option<Document>> {
    let doc = client
        .database(DB)
        .collection::<Document>(&collection)
        .find_one(filter)
        .await
        .unwrap();
    return Ok(doc);
}
