use std::{
    panic::catch_unwind,
    sync::{Arc, Mutex},
};

use anyhow::Result;
use bson::Document;
use futures::{future::join_all, TryStreamExt};
use indicatif::ProgressBar;
use mongodb::{
    options::{EstimatedDocumentCountOptions, FindOptions},
    Client,
};
use tokio::spawn;

use crate::points::{Coordinate, Elements, Patch};
use rayon::prelude::*;

const DB: &str = "ISRO";

pub async fn find_all_patches(
    client: Client,
    collection: String,
    filter: Document,
) -> Result<Vec<Patch>> {
    let count = client
        .database(DB)
        .collection::<Document>(collection.as_str())
        .estimated_document_count()
        .await
        .unwrap();

    let mut result = vec![];

    let mut cursor = client
        .database(DB)
        .collection::<Document>(collection.as_str())
        .find(filter)
        .limit(200000)
        .await
        .unwrap();

    println!("PARSING:");

    let bar = ProgressBar::new(count);

    while let Some(doc) = cursor.try_next().await? {
        let keys = vec![
            "V0_LAT", "V0_LON", "V1_LAT", "V1_LON", "V2_LAT", "V2_LON", "V3_LAT", "V3_LON",
        ];

        let all_keys_present = keys.par_iter().all(|x| doc.get_f64(*x).is_ok());

        if all_keys_present {
            result.push(Patch::new_from(
                vec![
                    Coordinate::new_from_lat_lon(
                        doc.get_f64("V0_LAT").unwrap(),
                        doc.get_f64("V0_LON").unwrap(),
                    ),
                    Coordinate::new_from_lat_lon(
                        doc.get_f64("V1_LAT").unwrap(),
                        doc.get_f64("V1_LON").unwrap(),
                    ),
                    Coordinate::new_from_lat_lon(
                        doc.get_f64("V2_LAT").unwrap(),
                        doc.get_f64("V2_LON").unwrap(),
                    ),
                    Coordinate::new_from_lat_lon(
                        doc.get_f64("V3_LAT").unwrap(),
                        doc.get_f64("V3_LON").unwrap(),
                    ),
                ],
                Elements::default(),
                Elements::default(),
            ));
            // println!("| FOUND | ObjectID: {:?}", doc.get_object_id("_id"));
        } else {
            println!("| NOT_PARSING | ObjectID: {:?}", doc.get_object_id("_id"));
        }
        bar.inc(1);
    }
    Ok(result)
}
