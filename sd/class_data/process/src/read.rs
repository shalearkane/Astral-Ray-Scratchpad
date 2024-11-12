use std::str::FromStr;
use std::sync::Arc;
use std::sync::Mutex;

use anyhow::{Ok, Result};
use bson::datetime::DateTimeBuilder;
use bson::doc;
use bson::Document;

extern crate fitrs;
use chrono::format::Parsed;
use chrono::Date;
use chrono::DateTime;
use chrono::Local;
use chrono::NaiveDateTime;
use chrono::NaiveTime;
use chrono::TimeZone;
use chrono::Utc;
use fitrs::{Fits, HeaderValue};
use mongodb::Client;
use rayon::iter::IndexedParallelIterator;
use rayon::iter::IntoParallelIterator;
use rayon::iter::ParallelIterator;
use rayon::slice::ParallelSlice;
use rayon::slice::ParallelSliceMut;
use tokio::runtime::Runtime;
use tokio::spawn;

use crate::mongo::insert_document;

// pub async fn read_fits(file_path: &str) -> Result<Vec<KeywordRecord<'_>>> {
//     let (_, fits) = parser::fits(fs::read(file_path).unwrap().as_ptr()).unwrap();
//     let hdus: Vec<fits_rs::types::HDU<'_>> = fits.extensions;
//     let mut headers = Vec::new();
//     if hdus.len() > 0 {
//         for key_idx in 0..hdus.get(0).unwrap().header.keyword_records.len() {
//             let key_record = hdus
//                 .get(0)
//                 .unwrap()
//                 .header
//                 .keyword_records
//                 .get(key_idx)
//                 .unwrap()
//                 .to_owned()
//                 .clone();
//             headers.push(KeywordRecord::new(
//                 key_record.keyword.clone(),
//                 key_record.value.clone(),
//                 key_record.comment.clone(),
//             ))
//         }
//     }
//     Ok(headers)
// }

fn get_file_extension(file_path: &str) -> Option<&str> {
    // Split the file path by '.' and get the last part as the extension if it exists
    let parts: Vec<&str> = file_path.split('.').collect();

    // Ensure there's an extension part and it's not the whole file name (like hidden files)
    if parts.len() > 1 && !file_path.ends_with('.') {
        parts.last().copied()
    } else {
        None
    }
}

/**
 * Takes input a time string and converts it to mongodb datetime
 */
pub fn str_to_datetime(time_str: &str) -> mongodb::bson::DateTime {
    let utc_time = NaiveDateTime::parse_from_str(time_str, "%Y%m%dT%H%M%S%f")
        .or(NaiveDateTime::parse_from_str(
            time_str,
            "%Y-%m-%dT%H:%M:%S.%f",
        ))
        .or(NaiveDateTime::parse_from_str(
            time_str,
            "%Y-%m-%d %H:%M:%S.%f",
        ))
        .unwrap_or_default()
        .and_utc();
    return mongodb::bson::DateTime::from_chrono(utc_time);
}

/**
 * Read fits file and returns a MongoDB Document with path of the file and the header metdatas
 */
pub fn read_fits(file_path: &str) -> Document {
    println!("| READING | {:?}", file_path);
    let fits = Fits::open(file_path).expect("Failed to open");
    let mut fits_doc = doc! {"path": file_path,"ext" : get_file_extension(file_path).unwrap()};
    for hdu in fits.iter() {
        for (header_type, header_value) in hdu.iter() {
            match header_value
                .unwrap_or(&HeaderValue::CharacterString(String::new()))
                .clone()
            {
                HeaderValue::CharacterString(value) => fits_doc.insert(header_type, value),
                HeaderValue::Logical(value) => fits_doc.insert(header_type, value),
                HeaderValue::ComplexIntegerNumber(real, img) => {
                    fits_doc.insert(header_type, vec![real, img])
                }
                HeaderValue::ComplexFloatingNumber(real, img) => {
                    fits_doc.insert(header_type, vec![real, img])
                }
                HeaderValue::RealFloatingNumber(value) => fits_doc.insert(header_type, value),
                HeaderValue::IntegerNumber(value) => fits_doc.insert(header_type, value),
            };
        }
    }

    if fits_doc.contains_key("STARTIME") || fits_doc.contains_key("DATE-OBS") {
        // let time = DateTime::from_str().unwrap().timestamp();
        fits_doc.insert(
            "parsedStartTime",
            str_to_datetime(
                fits_doc
                    .get_str("STARTIME")
                    .or(fits_doc.get_str("DATE-OBS"))
                    .unwrap(),
            ),
        );
    }

    if fits_doc.contains_key("ENDTIME") || fits_doc.contains_key("DATE-END") {
        // let time = DateTime::from_str().unwrap().timestamp();
        fits_doc.insert(
            "parsedEndTime",
            str_to_datetime(
                fits_doc
                    .get_str("ENDTIME")
                    .or(fits_doc.get_str("DATE-END"))
                    .unwrap(),
            ),
        );
    }
    fits_doc
}

pub async fn read_all_fits_files(
    client: Arc<Client>,
    file_paths: Arc<Mutex<Vec<String>>>,
    collection: String,
) -> Result<()> {
    file_paths
        .lock()
        .unwrap()
        .clone()
        .into_par_iter()
        .for_each(|file_path| {
            let document = read_fits(file_path.as_str());
            insert_document(client.clone(), document.clone(), collection.clone());
        });

    Ok(())
}
