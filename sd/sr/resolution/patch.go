package resolution

import (
	"log/slog"
	"math"
	"sr/geo"

	"github.com/schollz/progressbar/v3"
)

type PatchManager struct {
	PatchMap *map[string][]*geo.PointPixel
}

func NewPatchManager() *PatchManager {
	patchMap := make(map[string][]*geo.PointPixel)
	return &PatchManager{PatchMap: &patchMap}
}

func (pm *PatchManager) Search(pointPixel *geo.PointPixel) []*geo.PointPixel {
	var neighbouringPointPixels []*geo.PointPixel
	bound := pointPixel.BoundingBox.ToPolygon().RectBound()
	for lat := math.Floor(bound.Lo().Lat.Degrees()); lat <= math.Ceil(bound.Hi().Lat.Degrees()); lat = lat + 0.2 {
		for lon := math.Floor(bound.Lo().Lng.Degrees()); lon <= math.Ceil(bound.Hi().Lng.Degrees()); lon = lon + 0.2 {
			if (*pm.PatchMap)[GetTokenFromLatLonWithEvenBinning(lat, lon)] == nil {
				continue
			}

			neighbouringPointPixels = append(neighbouringPointPixels, (*pm.PatchMap)[GetTokenFromLatLonWithEvenBinning(lat, lon)]...)
		}
	}

	neighbourMap := make(map[string]bool)
	var uniqueNeighbours []*geo.PointPixel
	for _, neighbouringPointPixel := range neighbouringPointPixels {
		if neighbourMap[neighbouringPointPixel.ID] == false {
			uniqueNeighbours = append(uniqueNeighbours, neighbouringPointPixel)
			neighbourMap[neighbouringPointPixel.ID] = true
		}
	}

	return uniqueNeighbours
}

func (pm *PatchManager) ComputePatches(pointPixels []*geo.PointPixel) {
	slog.Info("--INDEXING--")
	bar := progressbar.Default(int64(len(pointPixels)))

	for _, pointPixel := range pointPixels {
		bound := pointPixel.BoundingBox.ToPolygon().RectBound()
		for lat := math.Floor(bound.Lo().Lat.Degrees()); lat <= math.Ceil(bound.Hi().Lat.Degrees()); lat = lat + 0.2 {
			for lon := math.Floor(bound.Lo().Lng.Degrees()); lon <= math.Ceil(bound.Hi().Lng.Degrees()); lon = lon + 0.2 {
				if (*pm.PatchMap)[GetTokenFromLatLonWithEvenBinning(lat, lon)] == nil {
					(*pm.PatchMap)[GetTokenFromLatLonWithEvenBinning(lat, lon)] = []*geo.PointPixel{}
				}

				(*pm.PatchMap)[GetTokenFromLatLonWithEvenBinning(lat, lon)] = append((*pm.PatchMap)[GetTokenFromLatLonWithEvenBinning(lat, lon)], pointPixel)
			}
		}
		bar.Add(1)
	}
	bar.Finish()
}
