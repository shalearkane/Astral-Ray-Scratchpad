use std::time::Duration;

use anyhow::Result;
use redis_work_queue::{Item, KeyPrefix, WorkQueue};

pub async fn listen_and_process(redis_uri: String) -> Result<()> {
    let db = &mut redis::Client::open(redis_uri)
        .unwrap()
        .get_async_connection()
        .await?;

    println!("----CONNECTED_TO_REDIS_QUEUE----");

    let work_queue = WorkQueue::new(KeyPrefix::from("example_work_queue"));

    loop {
        // Wait for a job with no timeout and a lease time of 5 seconds.
        let job: Item = work_queue
            .lease(db, None, Duration::from_secs(5))
            .await?
            .unwrap();
        process_job(&job);
        work_queue.complete(db, &job).await.unwrap();
    }
    Ok(())
}

fn process_job(job: &Item) {}
