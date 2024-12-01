use anyhow::{Ok, Result};
use bson::doc;
use chrono::Month;
use futures::future::try_join_all;
use log::info;
use mongodb::Client;
use redis_work_queue::{Item, KeyPrefix, WorkQueue};
use std::{
    borrow::{Borrow, BorrowMut},
    sync::Arc,
    time::Duration,
};
use tokio::spawn;

use crate::{mongo::find_one_and_replace, read::read_fits, unzip::unzip_file};

const DOWNLOAD_COMPLETE_QUEUE: &str = "DOWNLOAD_COMPLETE";
const FILE_PATH_TO_UNZIP_QUEUE: &str = "FILE_PATH_TO_UNZIP";
const DATA_UPLOADED_QUEUE: &str = "DATA_UPLOADED";

pub async fn listen_and_process(mongo: Arc<Client>, redis_uri: String) -> Result<()> {
    let mut handlers = vec![];
    handlers.push(spawn(listen_to_download_complete(mongo, redis_uri.clone())));
    handlers.push(spawn(listen_to_unzip_file(redis_uri)));
    try_join_all(handlers).await.unwrap();
    Ok(())
}

async fn listen_to_download_complete(mongo: Arc<Client>, redis_uri: String) -> Result<()> {
    info!("Starting to Consume {DOWNLOAD_COMPLETE_QUEUE}");
    let db = &mut redis::Client::open(redis_uri.clone())
        .unwrap()
        .get_async_connection()
        .await?;

    let work_queue = WorkQueue::new(KeyPrefix::from(DOWNLOAD_COMPLETE_QUEUE));

    loop {
        // Wait for a job with no timeout and a lease time of 5 seconds.
        let job: Item = work_queue
            .lease(db, None, Duration::from_secs(60 * 60))
            .await?
            .unwrap();
        spawn(upload_downloaded_files(
            mongo.clone(),
            redis_uri.clone(),
            String::from_utf8(job.data.to_vec()).unwrap(),
        ));
        work_queue.complete(db, &job).await.unwrap();
    }
}

async fn listen_to_unzip_file(redis_uri: String) -> Result<()> {
    info!("Starting to Consume {FILE_PATH_TO_UNZIP_QUEUE}");
    let db = &mut redis::Client::open(redis_uri.clone())
        .unwrap()
        .get_async_connection()
        .await?;

    let work_queue = WorkQueue::new(KeyPrefix::from(FILE_PATH_TO_UNZIP_QUEUE));

    loop {
        // Wait for a job with no timeout and a lease time of 5 seconds.
        let job: Item = work_queue
            .lease(db, None, Duration::from_secs(60 * 60))
            .await?
            .unwrap();
        spawn(unzip_file_from_path(
            redis_uri.clone(),
            String::from_utf8(job.data.to_vec()).unwrap(),
        ));
        work_queue.complete(db, &job).await.unwrap();
    }
}

async fn unzip_file_from_path(redis_uri: String, file_path: String) -> Result<()> {
    let db = &mut redis::Client::open(redis_uri)
        .unwrap()
        .get_async_connection()
        .await?;

    dbg!(file_path.clone());

    let download_data_queue = WorkQueue::new(KeyPrefix::from(DOWNLOAD_COMPLETE_QUEUE));
    let file_list = unzip_file(file_path, "../data/raw".to_string())
        .await
        .unwrap();

    for file in file_list {
        if !file.ends_with("xml") {
            download_data_queue
                .add_item(db, &Item::from_string_data(file))
                .await
                .unwrap();
        }
    }
    Ok(())
}

async fn upload_downloaded_files(
    mongo: Arc<Client>,
    redis_uri: String,
    file_path: String,
) -> Result<()> {
    let db = &mut redis::Client::open(redis_uri)
        .unwrap()
        .get_async_connection()
        .await?;

    let download_data_queue = WorkQueue::new(KeyPrefix::from(DOWNLOAD_COMPLETE_QUEUE));
    let data_uploaded_queue = WorkQueue::new(KeyPrefix::from(DATA_UPLOADED_QUEUE));

    if file_path.contains("xsm") {
        // Process xsm data
    } else {
        let doc = read_fits(file_path.as_str());

        let new_doc = find_one_and_replace(
            mongo.clone(),
            doc! {
                "path": doc.get_str("path").unwrap()
            },
            doc,
            "test".to_string(),
        )
        .await
        .unwrap();

        // Check if the document was successfully updated
        if new_doc.is_none() {
            // Not updated successfully so push to the queue again
            download_data_queue
                .add_item(db, &Item::from_string_data(file_path))
                .await
                .unwrap();
        } else {
            // Add the obj_id to the next queue to analyse
            let obj_id = new_doc.unwrap().get_object_id("_id").unwrap().to_string();
            data_uploaded_queue
                .add_item(db, &Item::from_string_data(obj_id))
                .await
                .unwrap();
        }
    }
    Ok(())
}
