use std::{ops::Deref, str};

use anyhow::{Ok, Result};
use imageproc::point::Point;

const NO_OF_LATITUDES: i32 = 180;
const NO_OF_LONGITUDES: i32 = 360;

#[derive(Debug, Copy, Clone)]
pub struct Coordinate {
    pub lat: f64,
    pub lon: f64,
}

#[derive(Debug, Clone)]
pub struct Patch {
    pub element: String,
    pub bounding_box: Vec<Coordinate>,
    pub intensity: f64,
}

impl Coordinate {
    pub fn new() -> Self {
        Coordinate {
            lon: f64::from_bits(0),
            lat: f64::from_bits(0),
        }
    }

    pub fn new_from_lat_lon(lat: f64, lon: f64) -> Self {
        Coordinate { lat, lon }
    }

    pub fn new_from_point(point: Point<i32>, image_height: i32, image_width: i32) -> Self {
        let lat_unit = f64::from(NO_OF_LATITUDES) / f64::from(image_height);
        let lon_unit = f64::from(NO_OF_LONGITUDES) / f64::from(image_width);
        return Coordinate {
            lat: (f64::from(NO_OF_LATITUDES) / f64::from(2)) - (f64::from(point.y) * lat_unit),
            lon: (f64::from(point.x) * lon_unit) - (f64::from(NO_OF_LONGITUDES) / f64::from(2)),
        };
    }

    pub fn to_point(&self, image_height: i32, image_width: i32) -> Point<i32> {
        let lat_unit = f64::from(NO_OF_LATITUDES) / f64::from(image_height);
        let lon_unit = f64::from(NO_OF_LONGITUDES) / f64::from(image_width);

        Point::<i32> {
            y: (((f64::from(NO_OF_LATITUDES) / f64::from(2)) - self.lat) / lat_unit).round() as i32,
            x: ((self.lon + f64::from(NO_OF_LONGITUDES) / f64::from(2)) / lon_unit).round() as i32,
        }
    }

    pub fn batch_convert_to_point(
        coordinates: Vec<Coordinate>,
        image_height: i32,
        image_width: i32,
    ) -> Result<Vec<Point<i32>>> {
        let mut points = vec![];
        for coordinate in coordinates {
            points.push(coordinate.to_point(image_height.clone(), image_width.clone()));
        }
        Ok(points)
    }
}

impl Patch {
    pub fn new() -> Self {
        Patch {
            element: String::new(),
            bounding_box: vec![],
            intensity: f64::from_bits(0),
        }
    }

    pub fn new_from(element: String, bounding_box: Vec<Coordinate>, intensity: f64) -> Self {
        Patch {
            element,
            bounding_box,
            intensity,
        }
    }

    fn get_bounding_box(&self) -> Vec<Coordinate> {
        let mut bounding_box = vec![];
        for coordinate in self.bounding_box.iter() {
            bounding_box.push(*coordinate);
        }
        return bounding_box;
    }

    pub fn get_bounding_box_points(
        &self,
        image_height: i32,
        image_width: i32,
    ) -> Result<Vec<Point<i32>>> {
        let bounding_box_points = Coordinate::batch_convert_to_point(
            self.bounding_box.clone(),
            image_height.clone(),
            image_width.clone(),
        )
        .unwrap();
        Ok(bounding_box_points)
    }
}
