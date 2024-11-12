extern crate redis;

use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use bson::doc;
use futures::stream::StreamExt;
use server::file_by_id;
use std::sync::{Arc, Mutex};
use tokio::spawn;

use anyhow::{Ok, Result};
use dashmap::DashMap;
use files::{get_all_file_ext, get_all_fits_files, get_dir_contents, recursive_get_contents};
use mongo::{find_one, insert_document};
use mongodb::{options::ClientOptions, Client};
// use queue::listen_and_process;
use read::{read_all_fits_files, read_fits};

mod files;
mod model;
mod mongo;
mod queue;
mod read;
mod server;

const REDIS_URI: &str = "redis://127.0.0.1:6379";

#[actix_web::main]
async fn main() -> Result<()> {
    /* FITS FILES */
    // let files = Arc::new(Mutex::new(Vec::new()));
    // get_all_fits_files("../../data/xsm/".to_string(), files.clone())
    //     .await
    //     .unwrap();

    let mongo = Client::with_options(
        ClientOptions::parse("mongodb://localhost:27017")
            .await
            .unwrap(),
    )
    .unwrap();

    // read_all_fits_files(Arc::new(mongo), files, "xsm_primary".to_string())
    //     .await
    //     .unwrap();

    // println!("| DONE | Scanning files");

    /* FILE EXTS */
    // let map = Arc::new(DashMap::new());
    // get_all_file_ext("../../data/xsm/".to_string(), map.clone())
    //     .await
    //     .unwrap();
    // dbg!(map);

    // fetch_all_class_docs(mongo).await.unwrap();

    // let insert = insert_document(Arc::new(mongo), fits_data).await.unwrap();

    // dbg!(read_fits("./test.lc"));

    // queue::listen_and_process(REDIS_URI.to_string())
    //     .await
    //     .unwrap();

    // dbg!(find_one(mongo, "test".to_string(), doc! {}).await.unwrap());

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(mongo.clone()))
            .service(file_by_id)
    })
    .workers(7)
    .bind(("0.0.0.0", 8081))?
    .run()
    .await
    .unwrap();
    Ok(())
}
