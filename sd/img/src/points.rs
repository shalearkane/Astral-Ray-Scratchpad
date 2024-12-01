use std::{ops::Deref, str};

use anyhow::{Ok, Result};
use geo::{Coord, LineString, Polygon};
use imageproc::point::Point;

const NO_OF_LATITUDES: i32 = 180;
const NO_OF_LONGITUDES: i32 = 360;

pub const PRECISION: f64 = 10.0;

#[derive(Debug, Copy, Clone, PartialEq)]
pub struct Coordinate {
    pub lat: f64,
    pub lon: f64,
}

#[derive(Debug, Copy, Clone, Default, PartialEq)]
pub struct Elements {
    pub mg: f64,
    pub al: f64,
    pub fe: f64,
    pub si: f64,
}

#[derive(Debug, Clone, Default, Copy)]
pub struct ElementsMap {
    pub wt: Elements,
    pub total_err: Elements,
}

#[derive(Debug, Clone, Default)]
pub struct Patch {
    pub bounding_box: Vec<Coordinate>,
    pub wt: Elements,
    pub total_err: Elements,
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
        Self::default()
    }

    pub fn new_from(bounding_box: Vec<Coordinate>, wt: Elements, total_err: Elements) -> Self {
        Patch {
            wt,
            bounding_box,
            total_err,
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

    pub fn get_bounding_box_geo_polygon(&self) -> Result<geo::Polygon<i32>> {
        Ok(Polygon::new(
            LineString::new(vec![
                Coord {
                    x: (self.bounding_box[0].lon * PRECISION) as i32,
                    y: (self.bounding_box[0].lat * PRECISION) as i32,
                },
                Coord {
                    x: (self.bounding_box[1].lon * PRECISION) as i32,
                    y: (self.bounding_box[1].lat * PRECISION) as i32,
                },
                Coord {
                    x: (self.bounding_box[2].lon * PRECISION) as i32,
                    y: (self.bounding_box[2].lat * PRECISION) as i32,
                },
                Coord {
                    x: (self.bounding_box[3].lon * PRECISION) as i32,
                    y: (self.bounding_box[3].lat * PRECISION) as i32,
                },
            ]),
            vec![],
        ))
    }
}

impl Elements {
    pub fn default_with(num: f64) -> Self {
        Elements {
            al: num,
            fe: num,
            mg: num,
            si: num,
        }
    }

    pub fn add(&self, element: Elements) -> Self {
        Elements {
            mg: self.mg + element.mg,
            al: self.al + element.al,
            fe: self.fe + element.fe,
            si: self.si + element.si,
        }
    }

    pub fn multiply(&self, element: Elements) -> Self {
        Elements {
            mg: self.mg * element.mg,
            al: self.al * element.al,
            fe: self.fe * element.fe,
            si: self.si * element.si,
        }
    }

    pub fn divide(&self, element: Elements) -> Self {
        Elements {
            mg: self.mg / element.mg,
            al: self.al / element.al,
            fe: self.fe / element.fe,
            si: self.si / element.si,
        }
    }

    pub fn is_zero(&self) -> bool {
        if *self == Elements::default_with(0.0) {
            return true;
        }
        return false;
    }
}
