package geo

import (
	"math"

	"github.com/golang/geo/r2"
	"github.com/golang/geo/s1"
	"github.com/golang/geo/s2"
)

// Geo represents a geographical point with latitude, longitude, and radius
type Geo struct {
	Lat    float64
	Lon    float64
	Radius float64
}

func NewGeoFromLatLon(lat, lon, radius float64) Geo {
	return Geo{lat, lon, radius}
}

func NewGeoFromLatLonWithUnitRadius(lat, lon float64) Geo {
	return Geo{lat, lon, 1.0}
}

func (g *Geo) ToGallPetersProjection() Coord {
	return NewCoord(
		g.Radius*g.Lon*PI/180.0,
		2.0*g.Radius*math.Sin(g.Lat*PI/180.0),
	)
}

func (g Geo) GetBoundingBox(padding float64) s2.Rect {
	pointsBoundingBox := g.ToGallPetersProjection().GetBoundingBox(padding)
	lo := CoordFromPoint(pointsBoundingBox.Lo()).
		ToGeo(g.Radius).ToLatLng()
	hi := CoordFromPoint(pointsBoundingBox.Hi()).
		ToGeo(g.Radius).
		ToLatLng()

	return s2.RectFromLatLng(lo).AddPoint(hi)
}

func (g Geo) GetBoundingPolygonBox(padding float64) *Box {
	rect := s2.RectFromCenterSize(g.ToLatLng(), s2.LatLngFromDegrees(padding, padding))

	centerTop := s2.Interpolate(0.5, s2.PointFromLatLng(rect.Vertex(2)), s2.PointFromLatLng(rect.Vertex(3)))
	centerBottom := s2.Interpolate(0.5, s2.PointFromLatLng(rect.Vertex(0)), s2.PointFromLatLng(rect.Vertex(1)))

	// Get the width right
	topRightPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), centerTop, s2.PointFromLatLng(rect.Vertex(2)))
	topLeftPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), centerTop, s2.PointFromLatLng(rect.Vertex(3)))
	bottomRightPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), centerBottom, s2.PointFromLatLng(rect.Vertex(1)))
	bottomLeftPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), centerBottom, s2.PointFromLatLng(rect.Vertex(0)))

	// leftHeight := topLeftPoint.Distance(bottomLeftPoint)
	// rightHeight := topRightPoint.Distance(bottomRightPoint)
	// height := centerTop.Distance(centerBottom)

	// Get the height right
	newTopRightPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), bottomRightPoint, topRightPoint)
	newBottomRightPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), topRightPoint, bottomRightPoint)
	newTopLeftPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), bottomLeftPoint, topLeftPoint)
	newBottomLeftPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), topLeftPoint, bottomLeftPoint)

	// newTopRightPoint := s2.InterpolateAtDistance(s1.Angle((padding+rightHeight.Degrees())/2), bottomRightPoint, topRightPoint)
	// newBottomRightPoint := s2.InterpolateAtDistance(s1.Angle((padding+rightHeight.Degrees())/2), topRightPoint, bottomRightPoint)
	// newTopLeftPoint := s2.InterpolateAtDistance(s1.Angle((padding+leftHeight.Degrees())/2), bottomLeftPoint, topLeftPoint)
	// newBottomLeftPoint := s2.InterpolateAtDistance(s1.Angle((padding+leftHeight.Degrees())/2), topLeftPoint, bottomLeftPoint)

	// // 2nd Approach
	// centerTop := s2.InterpolateAtDistance(s1.Angle((padding)/2), s2.PointFromLatLng(g.ToLatLng()), s2.PointFromLatLng(s2.LatLngFromDegrees(90, g.Lon)))
	// centerBottom := s2.InterpolateAtDistance(-s1.Angle((padding)/2), s2.PointFromLatLng(g.ToLatLng()), s2.PointFromLatLng(s2.LatLngFromDegrees(90, g.Lon)))
	// // centerLeft := s2.InterpolateAtDistance(s1.Angle((padding)/2), s2.PointFromLatLng(g.ToLatLng()), s2.PointFromLatLng(s2.LatLngFromDegrees(g.Lon, -180)))
	// // centerRight := s2.InterpolateAtDistance(s1.Angle((padding)/2), s2.PointFromLatLng(g.ToLatLng()), s2.PointFromLatLng(s2.LatLngFromDegrees(g.Lon, 180)))

	// newBottomLeftPoint := s2.InterpolateAtDistance(-s1.Angle(padding/2), centerBottom, s2.PointFromLatLng(s2.LatLngFromDegrees(float64(s2.LatLngFromPoint(centerBottom).Lat), 180)))
	// newBottomRightPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), centerBottom, s2.PointFromLatLng(s2.LatLngFromDegrees(float64(s2.LatLngFromPoint(centerBottom).Lat), 180)))
	// newTopRightPoint := s2.InterpolateAtDistance(-s1.Angle(padding/2), centerTop, s2.PointFromLatLng(s2.LatLngFromDegrees(float64(s2.LatLngFromPoint(centerTop).Lat), 180)))
	// newTopLeftPoint := s2.InterpolateAtDistance(s1.Angle(padding/2), centerTop, s2.PointFromLatLng(s2.LatLngFromDegrees(float64(s2.LatLngFromPoint(centerTop).Lat), 180)))

	// loop := s2.LoopFromPoints([]s2.Point{
	// 	newBottomLeftPoint, newBottomRightPoint, newTopRightPoint, newTopLeftPoint,
	// })

	// return *s2.PolygonFromLoops([]*s2.Loop{loop})
	return &Box{
		BottomLeft:  LatLonFromPoint(newBottomLeftPoint),
		BottomRight: LatLonFromPoint(newBottomRightPoint),
		TopLeft:     LatLonFromPoint(newTopLeftPoint),
		TopRight:    LatLonFromPoint(newTopRightPoint),
	}
}

func GetSubRectangles(boundingBox []Geo, sideLen, radius float64) []s2.Rect {
	subRectangles := []s2.Rect{}
	projectedSubRectangles := []r2.Rect{}
	sideLen = sideLen * 4.0 / PI

	minX, minY := 1e9, 1e9
	maxX, maxY := -1e9, -1e9

	for _, geo := range boundingBox {
		coord := geo.ToGallPetersProjection()
		if coord.X < minX {
			minX = coord.X
		}
		if coord.Y < minY {
			minY = coord.Y
		}
		if coord.X > maxX {
			maxX = coord.X
		}
		if coord.Y > maxY {
			maxY = coord.Y
		}
	}

	for x := minX; x <= maxX; x += sideLen {
		for y := minY; y <= maxY; y += sideLen {
			rect := r2.RectFromPoints(r2.Point{X: x, Y: y}, r2.Point{X: x, Y: y + sideLen}, r2.Point{X: x + sideLen, Y: y + sideLen}, r2.Point{X: x + sideLen, Y: y})
			projectedSubRectangles = append(projectedSubRectangles, rect)
		}
	}

	for _, projectedSubRectangle := range projectedSubRectangles {
		lo := CoordFromPoint(projectedSubRectangle.Lo()).
			ToGeo(radius).ToLatLng()
		hi := CoordFromPoint(projectedSubRectangle.Hi()).
			ToGeo(radius).
			ToLatLng()

		subRectangles = append(subRectangles, s2.RectFromLatLng(lo).AddPoint(hi))
	}

	return subRectangles
}

func (g Geo) ToLatLng() s2.LatLng {
	return s2.LatLngFromDegrees(g.Lat, g.Lon)
}
