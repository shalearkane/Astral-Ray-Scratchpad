package main

import (
	"math"
	"sr/fs"
	"sr/resolution"

	"github.com/k0kubun/pp/v3"
)

func main() {
	// pixels, err := fs.ReadJSONFile("./data.json")
	// if err != nil {
	// 	panic(err)
	// }

	// resManager := resolution.NewResolutionManager(pixels, constants.RADIUS, constants.PIXEL_LEN)

	// resManager.EnhancePixels()
	// resManager.SaveCSV("./output.csv")

	// polygon1 := gos.NewPolygonFromLoop(gos.NewLoopFromPath([]gos.Point{gos.PointFromLatLng(gos.LatLngFromDegrees(14.0, 10.0)), gos.PointFromLatLng(gos.LatLngFromDegrees(26.0, 20.0)), gos.PointFromLatLng(gos.LatLngFromDegrees(22.0, 25.0)), gos.PointFromLatLng(gos.LatLngFromDegrees(10.5, 25.0))}))
	// polygon2 := gos.NewPolygonFromLoop(gos.NewLoopFromPath([]gos.Point{gos.PointFromLatLng(gos.LatLngFromDegrees(10.0, 10.0)), gos.PointFromLatLng(gos.LatLngFromDegrees(26.0, 20.0)), gos.PointFromLatLng(gos.LatLngFromDegrees(24.0, 25.0)), gos.PointFromLatLng(gos.LatLngFromDegrees(12.0, 25.0))}))
	// // rect := s2.RectFromLatLng(s2.LatLngFromDegrees(10.0, 10.0)).AddPoint(s2.LatLngFromDegrees(26.0, 20.0)).AddPoint(s2.LatLngFromDegrees(24.0, 25.0))
	// polygon1.InitToIntersection(polygon1, polygon2)
	// loop := polygon1.Loop(0)
	// pp.Println(gos.LatLngFromPoint(*loop.Vertex(0)).String(), gos.LatLngFromPoint(*loop.Vertex(1)).String(), gos.LatLngFromPoint(*loop.Vertex(2)).String(), gos.LatLngFromPoint(*loop.Vertex(3)).String())
	//
	// geo := geo.NewGeoFromLatLonWithUnitRadius(-89.0, 11.0)
	// boundingPolygon := geo.GetBoundingPolygon(12.5 * 1e-5 * 180 / (math.Pi))
	// for li := 0; li < boundingPolygon.NumLoops(); li++ {
	// 	loop := boundingPolygon.Loop(li)
	// 	for vi := 0; vi < loop.NumVertices(); vi++ {
	// 		pp.Println(s2.LatLngFromPoint(loop.Vertex(vi)).String())
	// 	}
	// 	pp.Println("\n")
	// }
	//

	data, err := fs.ReadJSONFileToLatLngWt("./data.json")
	if err != nil {
		pp.Errorf(err.Error())
	}

	config := resolution.PointResolutionManagerConfig{
		LatLngs:     data,
		Radius:      1.0,
		SubPixelLen: 25 * 1e-5 * 180 / (math.Pi),
	}

	resManager := resolution.NewPointResolutionManager(config)
	resManager.EnhancePixels()
	resManager.SaveCSV("./output.csv")
}
