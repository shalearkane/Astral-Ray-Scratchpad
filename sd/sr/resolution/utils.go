package resolution

import (
	"fmt"
	"math"
	"strconv"

	"github.com/golang/geo/s2"
)

func RoundFloatWithEven(val float64) float64 {
	ratio := math.Pow(10, float64(1))
	if int(val*ratio)%2.0 != 0 {
		return ((val * ratio) + 1.0) / ratio
	}
	return (val * ratio) / ratio
}

func RoundFloat(val float64) float64 {
	ratio := math.Pow(10, float64(1))
	return math.Round(val*ratio) / 10.0
}

func getTokenFromBoundingBox(topLeft, bottomLeft, bottomRight, topRight s2.LatLng) string {
	return fmt.Sprintf("{%v_%v} , {%v_%v} , {%v_%v} , {%v_%v}", math.Round(topLeft.Lat.Degrees()), math.Round(topLeft.Lng.Degrees()), math.Round(bottomLeft.Lat.Degrees()), math.Round(bottomLeft.Lng.Degrees()), math.Round(bottomRight.Lat.Degrees()), math.Round(bottomRight.Lng.Degrees()), math.Round(topRight.Lat.Degrees()), math.Round(topRight.Lng.Degrees()))
}

func GetTokenFromLatLonWithEvenBinning(lat, lon float64) string {
	latStr := strconv.FormatFloat(RoundFloatWithEven(lat), 'f', 1, 64)
	lonStr := strconv.FormatFloat(RoundFloatWithEven(lon), 'f', 1, 64)
	return "{" + latStr + "_" + lonStr + "}"
}

func GetTokenFromLatLon(lat, lon float64) string {
	return fmt.Sprintf("{%v_%v}", RoundFloat(lat), RoundFloat(lon))
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
