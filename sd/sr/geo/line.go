package geo

import (
	"github.com/golang/geo/s1"
	"github.com/golang/geo/s2"
)

type Line struct {
	Start s2.Point
	End   s2.Point
}

func NewLine(start s2.Point, end s2.Point) Line {
	return Line{Start: start, End: end}
}

func (line Line) DistanceInLineFromStart(distance float64) s2.Point {
	distance = distance * 1e-5 * 180 / PI
	return s2.InterpolateAtDistance(s1.Angle(distance), line.Start, line.End)
}
