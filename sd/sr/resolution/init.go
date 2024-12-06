package resolution

import (
	"sr/constants"
	"sr/geo"

	"github.com/golang/geo/s2"
)

type PixelResolutionManager struct {
	Pixels []geo.RectPixel
}

func NewPixelResolutionManager(pixels []geo.RectPixel, radius, subPixelLen float64) *PixelResolutionManager {
	// Placeholder for sub-pixel computation logic
	var sub_pixels []geo.RectPixel
	for _, pixel := range pixels {
		subRectangles :=
			geo.GetSubRectangles(pixel.GetGeoBoundingBox(radius), constants.PIXEL_LEN, constants.RADIUS)

		for _, rectangle := range subRectangles {
			sub_pixels = append(sub_pixels, geo.NewRectPixel(&rectangle, pixel.Wt))
		}
	}

	return &PixelResolutionManager{Pixels: sub_pixels}
}

type PointResolutionManager struct {
	PointPixels  *[]*geo.PointPixel
	PatchManager *PatchManager
	SubPixelLen  float64
}

type LatLonWt struct {
	LatLngs s2.LatLng
	Wt      geo.Element
}

type PointResolutionManagerConfig struct {
	LatLngs     []*LatLonWt
	Radius      float64
	SubPixelLen float64
}

func NewPointResolutionManager(config PointResolutionManagerConfig) *PointResolutionManager {
	var pointPixels []*geo.PointPixel
	for _, latlng := range config.LatLngs {
		pointPixels = append(pointPixels, geo.NewPointPixel(latlng.LatLngs.Lat.Degrees(), latlng.LatLngs.Lng.Degrees(), latlng.Wt, config.SubPixelLen))
	}

	patchManager := NewPatchManager()
	patchManager.ComputePatches(pointPixels)

	return &PointResolutionManager{PointPixels: &pointPixels, PatchManager: patchManager, SubPixelLen: config.SubPixelLen}
}
