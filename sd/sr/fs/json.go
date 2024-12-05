package fs

import (
	"encoding/json"
	"os"
	"sr/constants"
	"sr/geo"
	"sr/resolution"

	"github.com/golang/geo/s2"
)

// Abundance represents the input JSON structure
type Abundance struct {
	Lat float64     `json:"lat"`
	Lon float64     `json:"lon"`
	Wt  geo.Element `json:"wt"`
}

// ReadJSONFile reads a JSON file and converts it to a list of Pixels
func ReadJSONFile(filePath string) ([]geo.RectPixel, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var abundances []Abundance
	if err := json.NewDecoder(file).Decode(&abundances); err != nil {
		return nil, err
	}

	var pixels []geo.RectPixel
	for _, abund := range abundances {
		boundingBox := geo.Geo{Lat: abund.Lat, Lon: abund.Lon, Radius: constants.RADIUS}.GetBoundingBox(constants.PIXEL_LEN)
		pixels = append(pixels, geo.RectPixel{
			BoundingBox: &boundingBox,
			Wt:          abund.Wt,
		})
	}
	return pixels, nil
}

func ReadJSONFileToLatLngWt(filePath string) ([]*resolution.LatLonWt, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var abundances []Abundance
	if err := json.NewDecoder(file).Decode(&abundances); err != nil {
		return nil, err
	}

	var latlons []*resolution.LatLonWt
	for _, abund := range abundances {
		latlons = append(latlons, &resolution.LatLonWt{
			LatLngs: s2.LatLngFromDegrees(abund.Lat, abund.Lon),
			Wt:      abund.Wt,
		})
	}
	return latlons, nil
}
