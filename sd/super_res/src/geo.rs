use std::f64::consts::PI;

use s2::latlng::LatLng;

#[derive(Clone, Copy, Debug, Default)]
pub struct Coord {
    pub x: f64,
    pub y: f64,
}

impl Coord {
    pub fn new(x: f64, y: f64) -> Self {
        Self { x, y }
    }

    pub fn from_point(point: s2::r2::point::Point) -> Self {
        Self {
            x: point.x,
            y: point.y,
        }
    }

    pub fn to_geo(&self, radius: f64) -> Geo {
        Geo::new_from_lat_lon(
            (self.y / (2.0 * radius)).asin().to_degrees(),
            (self.x / radius).to_degrees(),
            radius,
        )
    }

    pub fn get_bounding_box(&self, padding: f64) -> s2::r2::rect::Rect {
        s2::r2::rect::Rect::from_center_size(
            &s2::r2::point::Point::new(self.x, self.y),
            &s2::r2::point::Point::new(padding * 4.0 / PI, padding * 4.0 / PI),
        )
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct Geo {
    pub lat: f64,
    pub lon: f64,
    pub radius: f64,
}

impl Geo {
    pub fn new_from_lat_lon(lat: f64, lon: f64, radius: f64) -> Self {
        Self { lat, lon, radius }
    }

    pub fn to_lat_lng(&self) -> LatLng {
        LatLng::from_degrees(self.lat, self.lon)
    }

    pub fn to_gall_peters_projection(&self) -> Coord {
        Coord::new(
            self.radius * self.lon.to_radians(),
            2.0 * self.radius * self.lat.to_radians().sin(),
        )
    }

    pub fn get_bounding_box(&self, padding: f64) -> s2::rect::Rect {
        let points_bounding_box = self.to_gall_peters_projection().get_bounding_box(padding);
        let lo = Coord::from_point(points_bounding_box.lo())
            .to_geo(self.radius)
            .to_lat_lng();
        let hi = Coord::from_point(points_bounding_box.hi())
            .to_geo(self.radius)
            .to_lat_lng();
        s2::rect::Rect::from_point_pair(&lo, &hi)
    }

    pub fn get_sub_rectangles(
        bounding_box: Vec<Geo>,
        side_len: f64,
        radius: f64,
    ) -> Vec<s2::rect::Rect> {
        let mut sub_rectangles = Vec::new();
        let side_len = side_len * 4.0 / PI;
        let mut min_x = 1e9_f64;
        let mut min_y = 1e9_f64;
        let mut max_x = -1e9_f64;
        let mut max_y = -1e9_f64;
        for geo in bounding_box {
            let coord = geo.to_gall_peters_projection();
            min_x = min_x.min(coord.x);
            min_y = min_y.min(coord.y);
            max_x = max_x.max(coord.x);
            max_y = max_y.max(coord.y);
        }

        let mut projected_sub_rectangles: Vec<s2::r2::rect::Rect> = Vec::new();

        loop {
            let mut y = min_y;
            let x = min_x;

            loop {
                projected_sub_rectangles.push(s2::r2::rect::Rect::from_points(&[
                    s2::r2::point::Point::new(x, y),
                    s2::r2::point::Point::new(x, y + side_len),
                    s2::r2::point::Point::new(x + side_len, y + side_len),
                    s2::r2::point::Point::new(x + side_len, y),
                ]));

                y = y + side_len;

                if y > max_y {
                    break;
                }
            }

            min_x = min_x + side_len;

            if min_x > max_x {
                break;
            }
        }

        for projected_sub_rectangle in projected_sub_rectangles {
            let lo = Coord::from_point(projected_sub_rectangle.lo())
                .to_geo(radius)
                .to_lat_lng();
            let hi = Coord::from_point(projected_sub_rectangle.hi())
                .to_geo(radius)
                .to_lat_lng();
            sub_rectangles.push(s2::rect::Rect::from_point_pair(&lo, &hi));
        }

        sub_rectangles
    }
}
