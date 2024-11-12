use std::{
    env,
    ops::{Deref, DerefMut},
    path::Path,
    sync::{Arc, Mutex},
};

use anyhow::{Ok, Result};
use bson::doc;
use color::ColorManager;
use colorgrad::{Color, GradientBuilder, LinearGradient};
use futures::future::join_all;
use imageproc::{
    drawing::{draw_cross_mut, draw_line_segment_mut, draw_polygon_mut},
    image::{ImageBuffer, Rgb, RgbImage, Rgba, RgbaImage},
    point::Point,
};
use indicatif::ProgressBar;
use mongo::find_all_patches;
use mongodb::{options::ClientOptions, Client};
use points::{Coordinate, Patch};
use random_color::RandomColor;
use rayon::prelude::*;
use tokio::spawn;

mod color;
mod mongo;
mod points;

const IMAGE_HEIGHT: i32 = 1417;
const IMAGE_WIDTH: i32 = 2834;

async fn paint(
    image: Arc<Mutex<ImageBuffer<Rgba<u8>, Vec<u8>>>>,
    patch: Patch,
    color: Arc<ColorManager>,
    progress_bar: Arc<Mutex<ProgressBar>>,
) -> Result<()> {
    let bounding_box = patch
        .get_bounding_box_points(IMAGE_HEIGHT, IMAGE_WIDTH)
        .unwrap();
    if bounding_box[0] == bounding_box[bounding_box.len() - 1] {
        return Ok(());
    }

    let mut image_mut = image.lock();
    if image_mut.is_ok() {
        draw_polygon_mut(
            image_mut.unwrap().deref_mut(),
            bounding_box.as_slice(),
            Rgba(RandomColor::new().to_rgba_array()),
        );

        progress_bar.lock().unwrap().inc(1);
    }
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    let mongo = Client::with_options(
        ClientOptions::parse("mongodb://localhost:27017")
            .await
            .unwrap(),
    )
    .unwrap();

    let path = Path::new("./test1.png");
    // let patches: Vec<Patch> = vec![Patch::new_from(
    //     "element".to_string(),
    //     vec![
    //         Coordinate::new_from_lat_lon(50.4, 60.4),
    //         Coordinate::new_from_lat_lon(60.4, 60.4),
    //         Coordinate::new_from_lat_lon(-69.4, 50.4),
    //         Coordinate::new_from_lat_lon(50.4, 59.4),
    //     ],
    //     0.1,
    // )];

    let patches = find_all_patches(mongo, String::from("primary"), doc! {})
        .await
        .unwrap();

    let red = Rgb([255u8, 0u8, 0u8]);
    let green = Rgba([0u8, 255u8, 0u8, 255u8]);
    let blue = Rgb([0u8, 0u8, 255u8]);
    let white = Rgba([255u8, 255u8, 255u8, 255u8]);

    let color = Arc::new(ColorManager::new(green));
    let image = Arc::new(Mutex::new(RgbaImage::new(2834, 1417)));
    let mut handlers = vec![];

    println!("\n PAINTING: ");
    let bar = Arc::new(Mutex::new(ProgressBar::new(
        patches.len().try_into().unwrap(),
    )));

    for patch in patches {
        handlers.push(spawn(paint(
            image.clone(),
            patch,
            color.clone(),
            bar.clone(),
        )));
    }

    join_all(handlers).await;

    image.lock().unwrap().save(path).unwrap();

    Ok(())
}
