package resolution

import (
	"encoding/csv"
	"fmt"
	"os"

	"github.com/golang/geo/s2"
)

func (rm *PixelResolutionManager) SaveCSV(filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	headers := []string{"V0_LATITUDE", "V0_LONGITUDE", "V1_LATITUDE", "V1_LONGITUDE", "V2_LATITUDE", "V2_LONGITUDE", "V3_LATITUDE", "V3_LONGITUDE", "MG_WT", "AL_WT", "SI_WT", "FE_WT"}
	if err := writer.Write(headers); err != nil {
		return err
	}

	for _, pixel := range rm.Pixels {
		// Placeholder for converting bounding box vertices to lat/lon
		record := []string{
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(0).Lat.Degrees()),
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(0).Lng.Degrees()),
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(3).Lat.Degrees()),
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(3).Lng.Degrees()),
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(2).Lat.Degrees()),
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(2).Lng.Degrees()),
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(1).Lat.Degrees()),
			fmt.Sprintf("%f", pixel.BoundingBox.Vertex(1).Lng.Degrees()),
			fmt.Sprintf("%f", pixel.Wt.Mg),
			fmt.Sprintf("%f", pixel.Wt.Al),
			fmt.Sprintf("%f", pixel.Wt.Si),
			fmt.Sprintf("%f", pixel.Wt.Fe),
		}
		if err := writer.Write(record); err != nil {
			return err
		}
	}
	return nil
}

func (rm *PointResolutionManager) SaveCSV(filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	headers := []string{"V0_LATITUDE", "V0_LONGITUDE", "V1_LATITUDE", "V1_LONGITUDE", "V2_LATITUDE", "V2_LONGITUDE", "V3_LATITUDE", "V3_LONGITUDE", "MG_WT", "AL_WT", "SI_WT", "FE_WT"}
	if err := writer.Write(headers); err != nil {
		return err
	}

	for _, pixel := range rm.PointPixels {
		// Placeholder for converting bounding box vertices to lat/lon
		record := []string{
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(0)).Lat.Degrees()),
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(0)).Lng.Degrees()),
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(3)).Lat.Degrees()),
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(3)).Lng.Degrees()),
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(2)).Lat.Degrees()),
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(2)).Lng.Degrees()),
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(1)).Lat.Degrees()),
			fmt.Sprintf("%f", s2.LatLngFromPoint(pixel.BoundingBox.Loop(0).Vertex(1)).Lng.Degrees()),
			fmt.Sprintf("%f", pixel.Wt.Mg),
			fmt.Sprintf("%f", pixel.Wt.Al),
			fmt.Sprintf("%f", pixel.Wt.Si),
			fmt.Sprintf("%f", pixel.Wt.Fe),
		}
		if err := writer.Write(record); err != nil {
			return err
		}
	}
	return nil
}
