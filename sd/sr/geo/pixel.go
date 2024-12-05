package geo

import (
	"github.com/golang/geo/s2"
	"github.com/google/uuid"
)

type RectPixel struct {
	BoundingBox *s2.Rect
	Wt          Element
	ID          string
}

func NewRectPixel(boundingBox *s2.Rect, wt Element) RectPixel {
	return RectPixel{
		BoundingBox: boundingBox,
		Wt:          wt,
		ID:          uuid.NewString(),
	}
}

type ResolutionManager struct {
	Pixels []RectPixel
}

func (p *RectPixel) GetGeoBoundingBox(radius float64) []Geo {
	var geoBoundingBox []Geo
	for vertex_id := 0; vertex_id < 4; vertex_id = vertex_id + 1 {
		vertex := p.BoundingBox.Vertex(vertex_id)
		geoBoundingBox = append(geoBoundingBox, NewGeoFromLatLon(
			vertex.Lat.Degrees(),
			vertex.Lng.Degrees(),
			radius,
		))
	}
	return geoBoundingBox
}

type PointPixel struct {
	BoundingBox s2.Polygon
	Wt          Element
	ID          string
	Center      s2.LatLng
}

func NewPointPixel(lat float64, lon float64, wt Element, padding float64) *PointPixel {
	geo := NewGeoFromLatLon(lat, lon, 1.0)
	boundingBox := geo.GetBoundingPolygon(padding)
	return &PointPixel{
		BoundingBox: boundingBox,
		Wt:          wt,
		ID:          uuid.NewString(),
		Center:      s2.LatLngFromDegrees(lat, lon),
	}
}
