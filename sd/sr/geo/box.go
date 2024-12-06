package geo

import "github.com/golang/geo/s2"

type LatLon struct {
	Lat float64
	Lon float64
}

func LatLonFromPoint(point s2.Point) LatLon {
	latlng := s2.LatLngFromPoint(point)
	return LatLon{
		Lat: latlng.Lat.Degrees(),
		Lon: latlng.Lng.Degrees(),
	}
}

func (l *LatLon) ToLatLng() *s2.LatLng {
	latLng := s2.LatLngFromDegrees(l.Lat, l.Lon)
	return &latLng
}

type Box struct {
	BottomLeft  LatLon
	BottomRight LatLon
	TopLeft     LatLon
	TopRight    LatLon
}

func NewBox(newBottomLeftPoint, newBottomRightPoint, newTopRightPoint, newTopLeftPoint LatLon) *Box {
	return &Box{BottomLeft: newBottomLeftPoint, BottomRight: newBottomRightPoint, TopRight: newTopRightPoint, TopLeft: newTopLeftPoint}
}

func (box *Box) ToPolygon() *s2.Polygon {
	bottomLeft := s2.PointFromLatLng(s2.LatLngFromDegrees(box.BottomLeft.Lat, box.BottomLeft.Lon))
	bottomRight := s2.PointFromLatLng(s2.LatLngFromDegrees(box.BottomRight.Lat, box.BottomRight.Lon))
	topLeft := s2.PointFromLatLng(s2.LatLngFromDegrees(box.TopLeft.Lat, box.TopLeft.Lon))
	topRight := s2.PointFromLatLng(s2.LatLngFromDegrees(box.TopRight.Lat, box.TopRight.Lon))

	loop := s2.LoopFromPoints([]s2.Point{
		bottomLeft, bottomRight, topRight, topLeft,
	})

	return s2.PolygonFromLoops([]*s2.Loop{loop})
}
