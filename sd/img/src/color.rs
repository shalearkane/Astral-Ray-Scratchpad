use colorgrad::{Color, Gradient, GradientBuilder, LinearGradient};
use imageproc::image::Rgba;

pub struct ColorManager {
    pub end_color: Rgba<u8>,
    pub start_color: Rgba<u8>,
}

impl ColorManager {
    pub fn new(color: Rgba<u8>) -> Self {
        ColorManager {
            end_color: color,
            start_color: Rgba([255u8, 255u8, 255u8, 255u8]),
        }
    }

    /**
     * Returns the color for the intensity:
     * Note that the intensity must be between 0 - 1
     */
    pub fn get_color_for_intensity(&self, intensity: f32) -> Rgba<u8> {
        let r = (self.start_color[0] as f32 * (1.0 - intensity)
            + self.end_color[0] as f32 * intensity)
            .abs() as u8;
        let g = (self.start_color[1] as f32 * (1.0 - intensity)
            + self.end_color[1] as f32 * intensity)
            .abs() as u8;
        let b = (self.start_color[2] as f32 * (1.0 - intensity)
            + self.end_color[2] as f32 * intensity)
            .abs() as u8;
        let a = (self.start_color[3] as f32 * (1.0 - intensity)
            + self.end_color[3] as f32 * intensity)
            .abs() as u8;
        return Rgba([r, g, b, a]);
    }
}
