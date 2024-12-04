use std::sync::{Arc, Mutex};

use anyhow::{Ok, Result};
use csv::Writer;
use futures::future::join_all;
use indicatif::ProgressBar;
use nanoid::nanoid;
use serde::{Deserialize, Serialize};
use tokio::spawn;

use crate::geo::Geo;

#[derive(Clone, Copy, Debug, Default, PartialEq, Serialize, Deserialize)]
pub struct Element {
    pub al: f64,
    pub fe: f64,
    pub mg: f64,
    pub si: f64,
    pub na: f64,
    pub ca: f64,
    pub ti: f64,
    pub o: f64,
    pub norm: f64,
}

impl Element {
    pub fn default_with(n: f64) -> Self {
        Self {
            al: n,
            fe: n,
            mg: n,
            si: n,
            na: n,
            ca: n,
            ti: n,
            o: n,
            norm: n,
        }
    }

    pub fn multiply(&self, n: f64) -> Self {
        Self {
            al: self.al * n,
            fe: self.fe * n,
            mg: self.mg * n,
            si: self.si * n,
            na: self.na * n,
            ca: self.ca * n,
            ti: self.ti * n,
            o: self.o * n,
            norm: self.o * n,
        }
    }

    pub fn divide(&self, n: f64) -> Self {
        Self {
            al: self.al / n,
            fe: self.fe / n,
            mg: self.mg / n,
            si: self.si / n,
            na: self.na / n,
            ca: self.ca / n,
            ti: self.ti / n,
            o: self.o / n,
            norm: self.norm / n,
        }
    }

    pub fn add(&self, element: Element) -> Self {
        Self {
            al: self.al + element.al,
            fe: self.fe + element.fe,
            mg: self.mg + element.mg,
            si: self.si + element.si,
            na: self.na + element.na,
            ca: self.ca + element.ca,
            ti: self.ti + element.ti,
            o: self.o + element.o,
            norm: self.norm + element.norm,
        }
    }
}

#[derive(Clone, Debug)]
pub struct Pixel {
    bounding_box: s2::rect::Rect,
    wt: Element,
    id: String,
}

impl Pixel {
    pub fn new(bounding_box: s2::rect::Rect, wt: Element) -> Self {
        Self {
            bounding_box,
            wt,
            id: nanoid!(),
        }
    }

    pub fn default() -> Self {
        Self {
            bounding_box: s2::rect::Rect::empty(),
            wt: Element::default(),
            id: nanoid!(),
        }
    }

    pub fn from(pixel: Pixel) -> Self {
        Self {
            bounding_box: pixel.bounding_box,
            id: pixel.id,
            wt: pixel.wt,
        }
    }

    pub fn default_with_wt(n: f64) -> Self {
        Self {
            bounding_box: s2::rect::Rect::empty(),
            wt: Element::default_with(n),
            id: nanoid!(),
        }
    }

    pub fn get_geo_bounding_box(&self, radius: f64) -> Vec<Geo> {
        let mut geo_bounding_box = Vec::new();
        for vertex_id in 0..4 {
            let vertex = self.bounding_box.vertex(vertex_id);
            geo_bounding_box.push(Geo::new_from_lat_lon(
                vertex.lat.deg(),
                vertex.lng.deg(),
                radius,
            ));
        }
        geo_bounding_box
    }
}

#[derive(Clone, Debug, Default)]
pub struct ResolutionManager {
    pub pixels: Vec<Pixel>,
}

impl ResolutionManager {
    pub fn new(pixels: Vec<Pixel>, radius: f64, sub_pixel_len: f64) -> Self {
        let mut sub_pixels = Vec::new();
        for pixel in pixels {
            let sub_rectangles =
                Geo::get_sub_rectangles(pixel.get_geo_bounding_box(radius), sub_pixel_len, radius);

            for rectangle in sub_rectangles {
                sub_pixels.push(Pixel::new(rectangle, pixel.wt));
            }
        }
        Self { pixels: sub_pixels }
    }

    pub async fn enhance_pixels(&mut self) -> Result<()> {
        let enhanced_pixels = Arc::new(Mutex::new(Vec::new()));
        let mut handler = Vec::new();
        let progress = Arc::new(Mutex::new(ProgressBar::new(self.pixels.len() as u64)));
        for pixel in self.pixels.clone() {
            handler.push(spawn(ResolutionManager::enhance_pixel(
                Arc::new(pixel),
                Arc::new(self.pixels.clone()),
                enhanced_pixels.clone(),
                progress.clone(),
            )));
        }
        join_all(handler).await;

        let enhanced_pixels = enhanced_pixels.lock().unwrap().to_vec();
        self.pixels = enhanced_pixels;
        Ok(())
    }

    pub async fn enhance_pixel(
        pixel: Arc<Pixel>,
        all_pixels: Arc<Vec<Pixel>>,
        enhanced_pixels: Arc<Mutex<Vec<Pixel>>>,
        progress: Arc<Mutex<ProgressBar>>,
    ) -> Result<()> {
        let mut total_area = pixel.bounding_box.area();
        let mut wt = pixel.wt.multiply(total_area);

        for p in all_pixels.iter() {
            if p.id == pixel.id || !pixel.bounding_box.intersects(&p.bounding_box) {
                continue;
            }

            let area = pixel.bounding_box.intersection(&p.bounding_box).area();
            if area > 0.00107 {
                total_area = total_area + area;
                wt = wt.add(p.wt.multiply(area));
            }
        }

        wt = wt.divide(total_area);

        let new_pixel = Pixel {
            bounding_box: pixel.bounding_box.clone(),
            wt,
            id: pixel.id.clone(),
        };

        enhanced_pixels.lock().unwrap().push(new_pixel);
        progress.lock().unwrap().inc(1);
        Ok(())
    }

    pub fn save_csv(&self, filename: String) -> Result<()> {
        let mut wtr = Writer::from_path(filename)?;
        wtr.write_record(&[
            "V0_LATITUDE",
            "V0_LONGITUDE",
            "V1_LATITUDE",
            "V1_LONGITUDE",
            "V2_LATITUDE",
            "V2_LONGITUDE",
            "V3_LATITUDE",
            "V3_LONGITUDE",
            "MG_WT",
            "AL_WT",
            "SI_WT",
            "FE_WT",
        ])
        .unwrap();

        for pixel in self.pixels.iter() {
            let v0_lat = pixel.bounding_box.vertex(0).lat.deg().to_string();
            let v0_lon = pixel.bounding_box.vertex(0).lng.deg().to_string();
            let v1_lat = pixel.bounding_box.vertex(3).lat.deg().to_string();
            let v1_lon = pixel.bounding_box.vertex(3).lng.deg().to_string();
            let v2_lat = pixel.bounding_box.vertex(2).lat.deg().to_string();
            let v2_lon = pixel.bounding_box.vertex(2).lng.deg().to_string();
            let v3_lat = pixel.bounding_box.vertex(1).lat.deg().to_string();
            let v3_lon = pixel.bounding_box.vertex(1).lng.deg().to_string();
            let mg_wt = pixel.wt.mg.to_string();
            let al_wt = pixel.wt.al.to_string();
            let si_wt = pixel.wt.si.to_string();
            let fe_wt = pixel.wt.fe.to_string();
            wtr.write_record(&[
                v0_lat.as_str(),
                v0_lon.as_str(),
                v1_lat.as_str(),
                v1_lon.as_str(),
                v2_lat.as_str(),
                v2_lon.as_str(),
                v3_lat.as_str(),
                v3_lon.as_str(),
                mg_wt.as_str(),
                al_wt.as_str(),
                si_wt.as_str(),
                fe_wt.as_str(),
            ])
            .unwrap();
        }
        wtr.flush()?;

        Ok(())
    }
}
