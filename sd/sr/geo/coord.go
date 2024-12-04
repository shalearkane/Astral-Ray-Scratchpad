package geo

import (
	"math"

	"github.com/golang/geo/r2"
)

// Constants
const PI = math.Pi

// Coord represents a coordinate in 2D space
type Coord struct {
	X float64
	Y float64
}

func NewCoord(x, y float64) Coord {
	return Coord{x, y}
}

func CoordFromPoint(point r2.Point) Coord {
	return Coord{
		X: point.X,
		Y: point.Y,
	}
}

func (c Coord) ToGeo(radius float64) Geo {
	return NewGeoFromLatLon(
		math.Asin(c.Y/(2.0*radius))*180.0/PI,
		c.X/radius*180.0/PI,
		radius,
	)
}

func (c Coord) GetBoundingBox(padding float64) r2.Rect {
	return r2.RectFromCenterSize(
		r2.Point{X: c.X, Y: c.Y},
		r2.Point{X: padding * 4.0 / PI, Y: padding * 4.0 / PI},
	)
}
