use anyhow::{Ok, Result};
use bson::doc;
use bson::Document;

extern crate fitrs;
use chrono::NaiveDateTime;
use fitrs::{Fits, HeaderValue};

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
