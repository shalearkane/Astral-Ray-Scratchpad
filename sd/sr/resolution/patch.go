package resolution

import (
	"fmt"
	"log/slog"
	"math"
	"sr/geo"

	"github.com/golang/geo/s2"
	"github.com/schollz/progressbar/v3"
)

type PatchManager struct {
	PatchMap *map[string][]*geo.PointPixel
}

func roundFloatWithEven(val float64) float64 {
	ratio := math.Pow(10, float64(1))
	return math.RoundToEven(val*ratio) / ratio
}

func roundFloat(val float64) float64 {
	ratio := math.Pow(10, float64(1))
	return math.Round(val*ratio) / ratio
}

func getTokenFromBoundingBox(topLeft, bottomLeft, bottomRight, topRight s2.LatLng) string {
	return fmt.Sprintf("{%v_%v} , {%v_%v} , {%v_%v} , {%v_%v}", math.Round(topLeft.Lat.Degrees()), math.Round(topLeft.Lng.Degrees()), math.Round(bottomLeft.Lat.Degrees()), math.Round(bottomLeft.Lng.Degrees()), math.Round(bottomRight.Lat.Degrees()), math.Round(bottomRight.Lng.Degrees()), math.Round(topRight.Lat.Degrees()), math.Round(topRight.Lng.Degrees()))
}

func getTokenFromLatLonWithEvenBinning(lat, lon float64) string {
	return fmt.Sprintf("{%v_%v}", roundFloatWithEven(lat), roundFloatWithEven(lon))
}

func GetTokenFromLatLon(lat, lon float64) string {
	return fmt.Sprintf("{%v_%v}", roundFloat(lat), roundFloat(lon))
}

func UniqueSliceElements[T comparable](inputSlice []T) []T {
	uniqueSlice := make([]T, 0, len(inputSlice))
	seen := make(map[T]bool, len(inputSlice))
	for _, element := range inputSlice {
		if !seen[element] {
			uniqueSlice = append(uniqueSlice, element)
			seen[element] = true
		}
	}
	return uniqueSlice
}

func GetTokenFromPolygon(polygon *s2.Polygon) string {
	return getTokenFromBoundingBox(
		s2.LatLngFromPoint(polygon.Loop(0).Vertex(0)),
		s2.LatLngFromPoint(polygon.Loop(0).Vertex(1)),
		s2.LatLngFromPoint(polygon.Loop(0).Vertex(2)),
		s2.LatLngFromPoint(polygon.Loop(0).Vertex(3)),
	)
}

func NewPatchManager() *PatchManager {
	patchMap := make(map[string][]*geo.PointPixel)
	return &PatchManager{PatchMap: &patchMap}
}

func (pm *PatchManager) Search(pointPixel *geo.PointPixel) []*geo.PointPixel {
	var neighbouringPointPixels []*geo.PointPixel
	bound := pointPixel.BoundingBox.RectBound()
	for lat := math.Floor(bound.Lo().Lat.Degrees()); lat <= math.Ceil(bound.Hi().Lat.Degrees()); lat = lat + 0.2 {
		for lon := math.Floor(bound.Lo().Lng.Degrees()); lon <= math.Ceil(bound.Hi().Lng.Degrees()); lon = lon + 0.2 {
			if (*pm.PatchMap)[getTokenFromLatLonWithEvenBinning(lat, lon)] == nil {
				continue
			}

			neighbouringPointPixels = append(neighbouringPointPixels, (*pm.PatchMap)[getTokenFromLatLonWithEvenBinning(lat, lon)]...)
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
	slog.Info("INDEXING")
	bar := progressbar.Default(int64(len(pointPixels)))

	for _, pointPixel := range pointPixels {
		bound := pointPixel.BoundingBox.RectBound()
		for lat := math.Floor(bound.Lo().Lat.Degrees()); lat <= math.Ceil(bound.Hi().Lat.Degrees()); lat = lat + 0.2 {
			for lon := math.Floor(bound.Lo().Lng.Degrees()); lon <= math.Ceil(bound.Hi().Lng.Degrees()); lon = lon + 0.2 {
				if (*pm.PatchMap)[getTokenFromLatLonWithEvenBinning(lat, lon)] == nil {
					(*pm.PatchMap)[getTokenFromLatLonWithEvenBinning(lat, lon)] = []*geo.PointPixel{}
				}

				(*pm.PatchMap)[getTokenFromLatLonWithEvenBinning(lat, lon)] = append((*pm.PatchMap)[getTokenFromLatLonWithEvenBinning(lat, lon)], pointPixel)
			}
		}
		bar.Add(1)
	}
	bar.Finish()
}
