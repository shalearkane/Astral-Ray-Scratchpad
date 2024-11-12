use std::sync::Arc;

use actix_web::http::Error;
use anyhow::{Ok, Result};
use async_std::stream::StreamExt;
use bson::{doc, Document};
use mongodb::{
    action::InsertOne,
    results::{InsertManyResult, InsertOneResult},
    Client,
};
use rayon::collections;

use crate::{model::ClassModel, read::str_to_datetime};

const DB: &str = "ISRO";
const COLLECTION: &str = "primary";

pub fn insert_document(
    client: Arc<Client>,
    doc: Document,
    collection: String,
) -> Result<InsertOneResult> {
    let result = client
        .database(DB)
        .collection(collection.as_str())
        .insert_one(doc)
        .run()
        .unwrap();

    println!("| UPLOADED | {:?}", result.inserted_id);

    Ok(result)
}

pub fn insert_many_documents(client: Arc<Client>, doc: Vec<Document>) -> Result<InsertManyResult> {
    let result = client
        .database(DB)
        .collection(COLLECTION)
        .insert_many(doc)
        .run()
        .unwrap();

    println!("| UPLOADED | {:?}", result.inserted_ids);

    Ok(result)
}

pub async fn find_one(
    client: Arc<Client>,
    collection: String,
    filter: Document,
) -> Option<Result<Document, mongodb::error::Error>> {
    let mut cursor = client
        .database(DB)
        .collection::<Document>(&collection)
        .find(filter)
        .limit(1)
        .await
        .unwrap();
    return cursor.next().await;
}
