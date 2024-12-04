use std::{
    fs::{self, File},
    io::BufReader,
};

use anyhow::{Ok, Result};
use csv::{ReaderBuilder, Writer};
use s2::latlng::LatLng;
use serde::{Deserialize, Serialize};

use crate::{
    constants::{PADDING, RADIUS},
    geo::Geo,
    resolution::{Element, Pixel},
};

#[derive(Serialize, Deserialize, Debug)]
struct Abundance {
    lat: f64,
    lon: f64,
    wt: Element,
}

pub fn read_json_file(file_path: &str) -> Result<Vec<Pixel>> {
    let file = File::open(file_path)?;
    let reader = BufReader::new(file);
    let abundances: Vec<Abundance> = serde_json::from_reader(reader).unwrap();

    let mut pixels = Vec::new();
    for abund in abundances {
        let bounding_box =
            Geo::new_from_lat_lon(abund.lat, abund.lon, RADIUS).get_bounding_box(PADDING);
        pixels.push(Pixel::new(bounding_box, abund.wt));
    }

    Ok(pixels)
}

pub fn write_csv(filename: String, records: Vec<&[String]>) -> Result<()> {
    let mut wtr = Writer::from_path(filename)?;
    for record in records {
        wtr.write_record(record).unwrap()
    }
    wtr.flush()?;
    Ok(())
}

#[derive(Debug, Deserialize)]
struct CsvRecord {
    #[serde(rename = "V0_LATITUDE")]
    v0_latitude: f64,
    #[serde(rename = "V0_LONGITUDE")]
    v0_longitude: f64,
    #[serde(rename = "V1_LATITUDE")]
    v1_latitude: f64,
    #[serde(rename = "V1_LONGITUDE")]
    v1_longitude: f64,
    #[serde(rename = "V2_LATITUDE")]
    v2_latitude: f64,
    #[serde(rename = "V2_LONGITUDE")]
    v2_longitude: f64,
    #[serde(rename = "V3_LATITUDE")]
    v3_latitude: f64,
    #[serde(rename = "V3_LONGITUDE")]
    v3_longitude: f64,
    #[serde(rename = "MG_WT")]
    mg_wt: f64,
    #[serde(rename = "MG_FIT_UNC")]
    mg_fit_unc: f64,
    #[serde(rename = "MG_SYS_UNC")]
    mg_sys_unc: f64,
    #[serde(rename = "MG_TOT_UNC")]
    mg_tot_unc: f64,
    #[serde(rename = "AL_WT")]
    al_wt: f64,
    #[serde(rename = "AL_FIT_UNC")]
    al_fit_unc: f64,
    #[serde(rename = "AL_SYS_UNC")]
    al_sys_unc: f64,
    #[serde(rename = "AL_TOT_UNC")]
    al_tot_unc: f64,
    #[serde(rename = "SI_WT")]
    si_wt: f64,
    #[serde(rename = "SI_FIT_UNC")]
    si_fit_unc: f64,
    #[serde(rename = "SI_SYS_UNC")]
    si_sys_unc: f64,
    #[serde(rename = "SI_TOT_UNC")]
    si_tot_unc: f64,
    #[serde(rename = "FE_WT")]
    fe_wt: f64,
    #[serde(rename = "FE_FIT_UNC")]
    fe_fit_unc: f64,
    #[serde(rename = "FE_SYS_UNC")]
    fe_sys_unc: f64,
    #[serde(rename = "FE_TOT_UNC")]
    fe_tot_unc: f64,
}

pub fn read_csv_file(file_path: &str) -> Result<Vec<Pixel>> {
    // Open the CSV file
    let file = File::open(file_path)?;

    // Create a CSV reader with flexible configuration
    let mut rdr = ReaderBuilder::new()
        .has_headers(true) // assuming the file has headers
        .trim(csv::Trim::All) // trim spaces around headers and data
        .from_reader(file);

    let mut pixels = Vec::new();

    // Iterate over the records and deserialize into the struct
    for result in rdr.deserialize::<CsvRecord>() {
        let record: CsvRecord = result?;
        let pixel = Pixel::new(
            s2::rect::Rect::from_point_pair(
                &LatLng::from_degrees(record.v1_latitude, record.v1_longitude),
                &LatLng::from_degrees(record.v3_latitude, record.v3_longitude),
            ),
            Element {
                al: record.al_wt,
                fe: record.fe_wt,
                mg: record.mg_wt,
                si: record.si_wt,
                na: 0.0,
                ca: 0.0,
                ti: 0.0,
                o: 0.0,
                norm: 0.0,
            },
        );

        pixels.push(pixel);
    }

    Ok(pixels)
}
