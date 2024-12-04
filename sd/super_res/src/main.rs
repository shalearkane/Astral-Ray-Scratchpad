use std::str::FromStr;

use anyhow::{Ok, Result};
use constants::{PADDING, RADIUS};
use fs::{read_csv_file, read_json_file};
use resolution::{Element, Pixel, ResolutionManager};

mod constants;
mod fs;
mod geo;
mod resolution;

#[tokio::main]
async fn main() -> Result<()> {
    // let pixels = read_json_file("./data.json").unwrap();
    let pixels = read_csv_file("./data.csv").unwrap();
    let mut res_manager = ResolutionManager::new(
        // vec![
        //     Pixel::new(
        //         s2::rect::Rect::from_degrees(10.0, 10.0, 20.0, 20.0),
        //         Element::default_with(2.0),
        //     ),
        //     Pixel::new(
        //         s2::rect::Rect::from_degrees(5.0, 5.0, 15.0, 15.0),
        //         Element::default_with(4.0),
        //     ),
        //     Pixel::new(
        //         s2::rect::Rect::from_degrees(12.0, 12.0, 25.0, 25.0),
        //         Element::default_with(6.0),
        //     ),
        // ],
        pixels, RADIUS, PADDING,
    );

    res_manager.enhance_pixels().await.unwrap();

    res_manager
        .save_csv(String::from_str("./output.csv").unwrap())
        .unwrap();
    Ok(())
}
