package geo

import (
	gos "github.com/davidreynolds/gos2/s2"
	"github.com/golang/geo/s2"
	"github.com/k0kubun/pp/v3"
)

func GetS2PolygonVertexPoints(p s2.Polygon) []s2.Point {
	var vertices []s2.Point
	for li := 0; li < p.NumLoops(); li++ {
		loop := p.Loop(li)
		for vi := 0; vi < loop.NumVertices(); vi++ {
			vertices = append(vertices, loop.Vertex(vi))
		}
	}

	return vertices
}

func GetGos2PolygonVertexPoints(p gos.Polygon) []gos.Point {
	var vertices []gos.Point
	for li := 0; li < p.NumLoops(); li++ {
		loop := p.Loop(li)
		for vi := 0; vi < loop.NumVertices(); vi++ {
			vertices = append(vertices, *loop.Vertex(vi))
		}
	}

	return vertices
}

func ConvertGos2ToS2Polygon(polygon *gos.Polygon) s2.Polygon {
	var vertices []s2.Point
	for _, vertex := range GetGos2PolygonVertexPoints(*polygon) {
		vertices = append(vertices, ConvertGos2ToS2Point(vertex))
	}

	return *s2.PolygonFromLoops([]*s2.Loop{
		s2.LoopFromPoints(vertices),
	})
}

func ConvertS2ToGos2Point(point s2.Point) gos.Point {
	return gos.PointFromCoords(point.X, point.Y, point.Z)
}

func ConvertGos2ToS2Point(point gos.Point) s2.Point {
	return s2.PointFromCoords(point.X, point.Y, point.Z)
}

func GetPolygonAreaOfIntersection(a, b s2.Polygon) float64 {
	aVertices := GetS2PolygonVertexPoints(a)
	bVertices := GetS2PolygonVertexPoints(b)

	var aGosVertices []gos.Point
	var bGosVertices []gos.Point

	for _, point := range aVertices {
		aGosVertices = append(aGosVertices, ConvertS2ToGos2Point(point))
	}
	for _, point := range bVertices {
		bGosVertices = append(bGosVertices, ConvertS2ToGos2Point(point))
	}
	aPolygon := gos.NewPolygonFromLoop(gos.NewLoopFromPath(aGosVertices))
	bPolygon := gos.NewPolygonFromLoop(gos.NewLoopFromPath(bGosVertices))

	// Intersection
	aPolygon.InitToIntersection(aPolygon, bPolygon)

	intersectionPolygon := ConvertGos2ToS2Polygon(aPolygon)

	return intersectionPolygon.Area()
}

func PrintS2Polygon(polygon s2.Polygon) {
	for li := 0; li < polygon.NumLoops(); li++ {
		loop := polygon.Loop(li)
		for vi := 0; vi < loop.NumVertices(); vi++ {
			pp.Println(s2.LatLngFromPoint(loop.Vertex(vi)).String())
		}
	}
}

func PrintS2Rect(rect s2.Rect) {
	for li := 0; li < 4; li++ {
		pp.Println(rect.Vertex(li).String())
	}
}
