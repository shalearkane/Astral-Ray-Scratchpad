extern crate redis;

use actix_web::{web, App, HttpServer};
use redis_work_queue::{KeyPrefix, WorkQueue};
use server::file_by_id;
use std::sync::{Arc, Mutex};
use tokio::spawn;

use anyhow::{Ok, Result};
use mongodb::{options::ClientOptions, Client};

mod files;
mod model;
mod mongo;
mod queue;
mod read;
mod server;
mod unzip;

const REDIS_URI: &str = "redis://localhost:6379";

#[actix_web::main]
async fn main() -> Result<()> {
    colog::init();

    let mongo = Client::with_options(
        ClientOptions::parse("mongodb://localhost:27017")
            .await
            .unwrap(),
    )
    .unwrap();

    spawn(queue::listen_and_process(
        Arc::new(mongo.clone()),
        REDIS_URI.to_string(),
    ));

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
