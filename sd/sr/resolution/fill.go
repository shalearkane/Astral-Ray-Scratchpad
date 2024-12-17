package resolution

import (
	"log/slog"
	"sr/geo"
	"strconv"
	"sync"

	"github.com/k0kubun/pp/v3"
	"github.com/schollz/progressbar/v3"
)

type DCT struct {
	Matrix *[][]*geo.PointPixel
	Lat    float64
	Lon    float64
}

const CONTEXT_WINDOW = 16.0

// const LAT_START = -90.0
// const LAT_END = 90.0
// const LON_START = -180.0
// const LON_END = 180.0

func (pm *PointResolutionManager) GetPixelsToFill() (*map[string]*geo.PointPixel, *map[string]*geo.LatLon) {
	pixelsYetToBeProcessed := make(map[string]*geo.LatLon)

	slog.Info("--CALCULATING FILL STATISICS--")
	bar := progressbar.Default(int64(len(*pm.PointPixels)))
	pixelFound := map[string]*geo.PointPixel{}
	for _, pointPixel := range *pm.PointPixels {
		bound := pointPixel.BoundingBox.ToPolygon().RectBound()
		for lat := bound.Lo().Lat.Degrees(); lat <= bound.Hi().Lat.Degrees(); lat = lat + 0.2 {
			for lon := bound.Lo().Lng.Degrees(); lon <= bound.Hi().Lng.Degrees(); lon = lon + 0.2 {
				pixelFound[GetTokenFromLatLon(lat, lon)] = pointPixel
			}
		}
		bar.Add(1)
	}

	for lat := pm.Box.BottomLeft.Lat; lat <= pm.Box.TopLeft.Lat; lat = lat + 0.1 {
		for lon := pm.Box.BottomLeft.Lon; lon <= pm.Box.BottomRight.Lon; lon = lon + 0.1 {
			if pixelFound[GetTokenFromLatLon(lat, lon)] == nil {
				pixelsYetToBeProcessed[GetTokenFromLatLon(lat, lon)] = &geo.LatLon{
					Lat: lat,
					Lon: lon,
				}
			}
		}
	}

	return &pixelFound, &pixelsYetToBeProcessed
}

// Return array of matrices
func (pm *PointResolutionManager) GetClusters(pixelsFound *map[string]*geo.PointPixel, emptyLatLon *map[string]*geo.LatLon) []*DCT {
	var dcts []*DCT
	newEmptyLatlon := make(map[string]*geo.LatLon)

	slog.Info("-- CLUSTERING_V2 --")
	bar := progressbar.New(int(len(*emptyLatLon)))

	for _, latLon := range *emptyLatLon {
		if (*pixelsFound)[GetTokenFromLatLon(latLon.Lat, latLon.Lon)] != nil {
			bar.Add(1)
			continue
		}

		// Check if there are surrounding pixels
		top := (*pixelsFound)[GetTokenFromLatLon(latLon.Lat+0.1, latLon.Lon)]
		left := (*pixelsFound)[GetTokenFromLatLon(latLon.Lat, latLon.Lon-0.1)]
		right := (*pixelsFound)[GetTokenFromLatLon(latLon.Lat, latLon.Lon+0.1)]
		bottom := (*pixelsFound)[GetTokenFromLatLon(latLon.Lat-0.1, latLon.Lon)]

		zeroWt := geo.NewElementWithDefault(0.0)
		newPointPixel := &geo.PointPixel{
			Wt: &zeroWt,
			Center: geo.LatLon{
				Lat: latLon.Lat,
				Lon: latLon.Lon,
			},
		}

		if top != nil || left != nil || right != nil || bottom != nil {
			// Create a offset
			pixelPoint := top
			if pixelPoint == nil {
				pixelPoint = left
			}
			if pixelPoint == nil {
				pixelPoint = right
			}
			if pixelPoint == nil {
				pixelPoint = bottom
			}

			latOffset := (latLon.Lat - pixelPoint.Center.Lat) * 0.2
			lonOffset := (latLon.Lon - pixelPoint.Center.Lon) * 0.2

			// Create the DCT matrix -> 0.4 lat | lon consists of one matrix
			dctMatrix := [][]*geo.PointPixel{}
			// minDiffLat := 1e9
			// minDiffLon := 1e9
			// offsetedLat := 0
			// offsetedLon := 0

			for i := 0; i < CONTEXT_WINDOW; i++ {
				dctMatrixRow := []*geo.PointPixel{}
				for j := 0; j < CONTEXT_WINDOW; j++ {

					lat := latLon.Lat + ((1.6 / CONTEXT_WINDOW) * float64(i)) - 0.8 - latOffset
					lon := latLon.Lon + ((1.6 / CONTEXT_WINDOW) * float64(j)) - 0.8 - lonOffset

					token := GetTokenFromLatLon(lat, lon)
					newPixelFound := (*pixelsFound)[token]
					if newPixelFound == nil {
						dctMatrixRow = append(dctMatrixRow, newPointPixel)
					} else {
						dctMatrixRow = append(dctMatrixRow, newPixelFound)
					}
				}

				dctMatrix = append(dctMatrix, dctMatrixRow)
			}

			// Fill this pixel as neighbours are found
			// for lat := latLon.Lat - 0.2; lat <= latLon.Lat+0.2; lat += 0.1 {
			// 	for lon := latLon.Lon - 0.2; lon <= latLon.Lon+0.2; lon += 0.1 {
			// 		(*pixelsFound)[GetTokenFromLatLon(lat, lon)] = newPointPixel
			// 	}
			// }

			dcts = append(dcts, &DCT{
				Matrix: &dctMatrix,
				Lat:    latLon.Lat,
				Lon:    latLon.Lon,
			})
		} else {
			newEmptyLatlon[GetTokenFromLatLon(latLon.Lat, latLon.Lon)] = &geo.LatLon{
				Lat: latLon.Lat,
				Lon: latLon.Lon,
			}
		}

		bar.Add(1)
	}

	(*emptyLatLon) = newEmptyLatlon

	return dcts
}

// func (pm *PointResolutionManager) GetEmptyPixels() *map[string]*geo.PointPixel {
// 	emptyPixels := make(map[string]*geo.PointPixel)
// 	pixelFound := make(map[string]bool)

// 	slog.Info("--CALCULATING FILL STATISICS--")
// 	bar := progressbar.Default(int64(len(*pm.PointPixels)))

// 	for _, pointPixel := range *pm.PointPixels {
// 		bound := pointPixel.BoundingBox.ToPolygon().RectBound()
// 		for lat := bound.Lo().Lat.Degrees(); lat <= bound.Hi().Lat.Degrees(); lat = lat + 0.1 {
// 			for lon := bound.Lo().Lng.Degrees(); lon <= bound.Hi().Lng.Degrees(); lon = lon + 0.1 {
// 				if pixelFound[GetTokenFromLatLonWithEvenBinning(lat, lon)] == false {
// 					pixelFound[GetTokenFromLatLonWithEvenBinning(lat, lon)] = true
// 				}
// 			}
// 		}
// 		bar.Add(1)
// 	}

// 	// for lat := -90.0; lat <= 90.0; lat = lat + 0.2 {
// 	// 	for lon := -180.0; lon <= 180.0; lon = lon + 0.2 {
// 	// 		if pixelFound[getTokenFromLatLonWithEvenBinning(lat, lon)] == false {
// 	// 			pointPixel := geo.NewPointPixel(lat, lon, geo.NewElementWithDefault(10.0), pm.SubPixelLen)
// 	// 			emptyPixels[pointPixel.ID] = pointPixel
// 	// 		}
// 	// 	}
// 	// }
// 	for lat := 30.0; lat <= 50.0; lat = lat + 0.2 {
// 		for lon := 80.0; lon <= 100.0; lon = lon + 0.2 {
// 			if pixelFound[GetTokenFromLatLonWithEvenBinning(lat, lon)] == false {
// 				pointPixel := geo.NewPointPixel(lat, lon, geo.NewElementWithDefault(10.0), pm.SubPixelLen)
// 				emptyPixels[GetTokenFromLatLonWithEvenBinning(lat, lon)] = pointPixel
// 			}
// 		}
// 	}

// 	return &emptyPixels
// }

// func ClusterPixels(pointPixels *map[string]*geo.PointPixel) *[]*map[string]*geo.PointPixel {
// 	var clusters []*map[string]*geo.PointPixel
// 	processed := make(map[string]bool)

// 	slog.Info("-- CLUSTERING --")
// 	bar := progressbar.Default(int64(len(*pointPixels)))

// 	for _, pixel := range *pointPixels {
// 		token := GetTokenFromLatLonWithEvenBinning(pixel.Center.Lat, pixel.Center.Lon)

// 		if processed[token] {
// 			bar.Add(1)
// 			continue
// 		}

// 		pixelMap := map[string]*geo.PointPixel{
// 			token: pixel,
// 		}
// 		bound := pixel.BoundingBox.ToPolygon().RectBound()

// 		for lat := bound.Lo().Lat.Degrees(); lat <= bound.Hi().Lat.Degrees(); lat = lat + 0.2 {
// 			for lon := math.Floor(bound.Lo().Lng.Degrees()); lon <= math.Ceil(bound.Hi().Lng.Degrees()); lon = lon + 0.2 {
// 				foundPixel := (*pointPixels)[GetTokenFromLatLonWithEvenBinning(lat, lon)]
// 				if foundPixel != nil {
// 					foundPixelTokem := GetTokenFromLatLonWithEvenBinning(foundPixel.Center.Lat, foundPixel.Center.Lon)
// 					pixelMap[foundPixelTokem] = foundPixel
// 					processed[foundPixelTokem] = true
// 				}
// 			}
// 		}

// 		clusters = append(clusters, &pixelMap)
// 		bar.Add(1)
// 	}

// 	return &clusters
// }

// func (rm *PointResolutionManager) GetDCTCompatibleBoundingBox(emptyPixelsMap *map[string]*geo.PointPixel) (*[][]*geo.PointPixel, float64, float64) {
// 	var outputPointPixelMatrix [][]*geo.PointPixel

// 	maxLat := -1e9
// 	maxLon := -1e9
// 	minLon := 1e9
// 	minLat := 1e9

// 	for _, pointPixel := range *emptyPixelsMap {
// 		maxLat = math.Max(maxLat, pointPixel.Center.Lat)
// 		maxLon = math.Max(maxLon, pointPixel.Center.Lon)
// 		minLat = math.Min(minLat, pointPixel.Center.Lat)
// 		minLon = math.Min(minLon, pointPixel.Center.Lon)
// 	}

// 	// sideLen := math.Pow(2, math.Ceil(math.Log2(math.Max(maxLon-minLon, maxLat-minLat)*5)))
// 	sideLen := 32
// 	zeros := 0
// 	for i := 0; i < int(sideLen); i++ {
// 		lat := minLat + (float64(i) * 0.2)

// 		var row []*geo.PointPixel
// 		for j := 0; j < int(sideLen); j++ {
// 			lon := minLon + (float64(j) * 0.2)
// 			token := GetTokenFromLatLon(lat, lon)
// 			found := (*rm.PatchManager.PatchMap)[token]
// 			if found != nil && len(found) > 0 {
// 				row = append(row, found[0])
// 			} else {
// 				defaultElement := geo.NewElementWithDefault(0.0)
// 				row = append(row, &geo.PointPixel{Wt: &defaultElement})
// 			}

// 			if (*emptyPixelsMap)[token] == nil {
// 				delete(*emptyPixelsMap, token)
// 				zeros++
// 			}
// 		}

// 		outputPointPixelMatrix = append(outputPointPixelMatrix, row)
// 	}

// 	return &outputPointPixelMatrix, minLat, minLon
// }

// func (rm *PointResolutionManager) PatchImageWithDCTOutput(dctMatrix *[][]*geo.PointPixel, minLat, minLon float64, mutex *sync.Mutex) {
// 	for i, row := range *dctMatrix {
// 		lat := minLat + (float64(i) * 0.2)
// 		for j, pixel := range row {
// 			lon := minLon + (float64(j) * 0.2)
// 			token := GetTokenFromLatLon(lat, lon)
// 			mutex.Lock()
// 			found := (*rm.PatchManager.PatchMap)[token]
// 			if found == nil {
// 				(*rm.PatchManager.PatchMap)[token] = []*geo.PointPixel{pixel}
// 				(*rm.PointPixels) = append(*rm.PointPixels, geo.NewPointPixel(lat, lon, *pixel.Wt, rm.SubPixelLen))
// 			}
// 			mutex.Unlock()
// 		}
// 	}
// }

func (rm *PointResolutionManager) PatchImageAfterDCT(dct *DCT, dctOutput *[][]*geo.PointPixel, mutex *sync.Mutex, pixelsFound *map[string]*geo.PointPixel) {
	token := GetTokenFromLatLon(dct.Lat, dct.Lon)
	pointPixel := geo.NewPointPixel(dct.Lat, dct.Lon, *(*dctOutput)[CONTEXT_WINDOW/2][CONTEXT_WINDOW/2].Wt, rm.SubPixelLen)

	mutex.Lock()
	(*rm.PatchManager.PatchMap)[token] = []*geo.PointPixel{pointPixel}
	(*rm.PointPixels) = append(*rm.PointPixels, pointPixel)
	mutex.Unlock()

	for lat := dct.Lat - 0.2; lat <= dct.Lat+0.2; lat += 0.1 {
		for lon := dct.Lon - 0.2; lon <= dct.Lon+0.2; lon += 0.1 {
			mutex.Lock()
			(*pixelsFound)[GetTokenFromLatLon(lat, lon)] = pointPixel
			mutex.Unlock()
		}
	}
}

func (pm *PointResolutionManager) Fill() {
	// emptyPixelsMap := pm.GetEmptyPixels()

	// remaining := 0

	pixelFound, pixelsYetToBeProcessed := pm.GetPixelsToFill()

	// pp.Println(len(*pixelFound), len(*pixelsYetToBeProcessed), len(dcts))

	dcts := pm.GetClusters(pixelFound, pixelsYetToBeProcessed)

	var publishWg sync.WaitGroup
	for len(dcts) > 0 {
		pp.Println("ANALYSING " + strconv.Itoa(len(dcts)) + " | LEFT : " + strconv.Itoa(len(*pixelsYetToBeProcessed)))
		for _, chunk := range chunkBy(dcts, 200) {
			var wg sync.WaitGroup
			var mutex sync.Mutex
			for _, dct := range chunk {
				wg.Add(1)
				go func(dct *DCT, wg *sync.WaitGroup, mutex *sync.Mutex, pixelFound *map[string]*geo.PointPixel) {
					defer wg.Done()
					// dctMatrix, minLat, minLon := pm.GetDCTCompatibleBoundingBox(cluster)
					dctOutput := RunDCTFilling(dct.Matrix)
					pm.PatchImageAfterDCT(dct, dctOutput, mutex, pixelFound)
				}(dct, &wg, &mutex, pixelFound)
			}

			wg.Wait()

			publishWg.Add(1)
			go pm.PublishWithEnhancement(&publishWg)

		}

		// Update the dcts for next batch
		dcts = pm.GetClusters(pixelFound, pixelsYetToBeProcessed)
	}

	publishWg.Wait()

	// for len(*emptyPixelsMap) > 0 && len(*emptyPixelsMap) != remaining {
	// 	remaining = len(*emptyPixelsMap)
	// 	clusters := ClusterPixels(emptyPixelsMap)
	// 	pp.Println(len(*clusters))

	// 	for _, cluster := range *clusters {
	// 		wg.Add(1)
	// 		go func(wg *sync.WaitGroup, mutex *sync.Mutex) {
	// 			defer wg.Done()
	// 			dctMatrix, minLat, minLon := pm.GetDCTCompatibleBoundingBox(cluster)
	// 			dctOutput := RunDCTFilling(dctMatrix)
	// 			pm.PatchImageWithDCTOutput(dctOutput, minLat, minLon, mutex)
	// 		}(&wg, &mutex)
	// 	}

	// 	wg.Wait()
	// }

	// pixelsToFill := len(*emptyPixelsMap)
	// for i := 1; len(*emptyPixelsMap) > 0; i++ {
	// 	slog.Info("-- PIXELS TO FILL : " + strconv.Itoa(len(*emptyPixelsMap)) + " | ITER NO : " + strconv.Itoa(i))
	// 	pm.EnhanceAdditionalPixels(emptyPixelsMap)
	// 	// emptyPixels = pm.GetEmptyPixels()

	// 	if pixelsToFill == len(*emptyPixelsMap) {
	// 		slog.Error("FILLING FAILED")
	// 		return
	// 	}

	// 	pixelsToFill = len(*emptyPixelsMap)
	// }
}
