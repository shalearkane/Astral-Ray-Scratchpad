package main

import (
	"fmt"
	"math"

	geo "sr/geo"

	"github.com/golang/geo/s2"
)

// Convert latitude and longitude (degrees) to s2.Point
func latLonToPoint(lat, lon float64) s2.Point {
	return s2.PointFromLatLng(s2.LatLngFromDegrees(lat, lon))
}

// Create an s2.Loop (representing a spherical polygon) from a list of lat/lon coordinates
func createSphericalPolygon(coords [4][2]float64) *s2.Loop {
	points := make([]s2.Point, len(coords))
	for i, coord := range coords {
		points[i] = latLonToPoint(coord[0], coord[1])
	}
	loop := s2.LoopFromPoints(points)
	loop.Normalize() // Ensure the loop is well-formed
	return loop
}

func computeOverlapArea(quad1, quad2 [4][2]float64) float64 {
	// Create s2.Loops for the two quadrilaterals
	loop1 := createSphericalPolygon(quad1)
	loop2 := createSphericalPolygon(quad2)

	// Create s2.Polygons from the loops
	poly1 := s2.PolygonFromLoops([]*s2.Loop{loop1})
	poly2 := s2.PolygonFromLoops([]*s2.Loop{loop2})

	// Compute the intersection of the two polygons
	intersectionAreaSteradians := geo.GetPolygonAreaOfIntersection(*poly1, *poly2)

	// Calculate the area of the intersection in steradians

	// Convert steradians to square meters (Earth radius = 6371 km)
	moonRadius := 1737.5 // in meters
	overlapAreaMeters := intersectionAreaSteradians * math.Pow(moonRadius, 2)

	return overlapAreaMeters
}

func main() {
	quad1 := [4][2]float64{
		{0, 0},
		{0, 0.41},
		{0.41, 0.41},
		{0.41, 0},
	}
	quad2 := [4][2]float64{
		{0, 0},
		{0, 0.41},
		{0.41, 0.41},
		{0.41, 0},
	}

	// Compute the overlap area
	overlapArea := computeOverlapArea(quad1, quad2)
	fmt.Printf("Overlap Area: %.2f square meters\n", overlapArea)
}
