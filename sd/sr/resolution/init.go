package resolution

import (
	"sr/constants"
	"sr/geo"
	"sync"

	"github.com/barkimedes/go-deepcopy"
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
	PointPixels   *[]*geo.PointPixel
	PatchManager  *PatchManager
	SubPixelLen   float64
	JobID         string
	ClientID      string
	UpdateChannel (chan *PointResolutionManager)
	Finished      bool
	Box           geo.Box
}

type LatLonWt struct {
	LatLngs s2.LatLng
	Wt      geo.Element
}

type PointResolutionManagerConfig struct {
	JobID         string
	ClientID      string
	UpdateChannel (chan *PointResolutionManager)
	LatLngs       []*LatLonWt
	Radius        float64
	SubPixelLen   float64
	Box           geo.Box
}

func NewPointResolutionManager(config PointResolutionManagerConfig) *PointResolutionManager {
	var pointPixels []*geo.PointPixel
	for _, latlng := range config.LatLngs {
		pointPixels = append(pointPixels, geo.NewPointPixel(latlng.LatLngs.Lat.Degrees(), latlng.LatLngs.Lng.Degrees(), latlng.Wt, config.SubPixelLen))
	}

	patchManager := NewPatchManager()
	patchManager.ComputePatches(pointPixels)

	return &PointResolutionManager{
		PointPixels:   &pointPixels,
		PatchManager:  patchManager,
		SubPixelLen:   config.SubPixelLen,
		JobID:         config.JobID,
		ClientID:      config.ClientID,
		UpdateChannel: config.UpdateChannel,
		Finished:      false,
		Box:           config.Box,
	}
}

func (rm *PointResolutionManager) PublishWithEnhancement(wg *sync.WaitGroup) {
	defer wg.Done()
	newRM := &PointResolutionManager{
		PointPixels:   deepcopy.MustAnything(rm.PointPixels).(*[]*geo.PointPixel),
		PatchManager:  deepcopy.MustAnything(rm.PatchManager).(*PatchManager),
		SubPixelLen:   rm.SubPixelLen,
		JobID:         rm.JobID,
		ClientID:      rm.ClientID,
		UpdateChannel: rm.UpdateChannel,
		Finished:      false,
		Box:           rm.Box,
	}

	newRM.EnhancePixels()
	(*rm).UpdateChannel <- newRM
}
