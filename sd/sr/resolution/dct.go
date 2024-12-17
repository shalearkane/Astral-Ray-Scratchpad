package resolution

import (
	"math"
	"sr/geo"
	"sync"

	gFourier "github.com/ardabasaran/go-fourier"
	"github.com/barkimedes/go-deepcopy"
	"github.com/golang/geo/s2"
	"github.com/schollz/progressbar/v3"
)

/*
*
@param sampleImg: It is same as y(n,m)
returns [](k,l) -> (k,l) being cooordinates of the missing point
*/
func GetMissingPixels(sampledImg *[][]float64) [][]int {
	var missingPoints [][]int

	for rowIdx, row := range *sampledImg {
		for colIdx, pixel := range row {
			if pixel == 0.0 {
				missingPoints = append(missingPoints, []int{rowIdx, colIdx})
			}
		}
	}

	return missingPoints
}

/*
*
Takes input the frequency domain matrix and gives its L1 norm
*/
func Get2DL1Norm(matrix [][]float64) float64 {
	sum := 0.0

	for _, row := range matrix {
		for _, cell := range row {
			sum += math.Abs(cell)
		}
	}

	return sum
}

/*
* @param sampleImg Same as sampled image
@missingPoints -> [](k,l)
delta -> Step size for calculating gradient
mu -> Step size to iteration in gradient descent
returns new Sample image -> For Next Process (iteration)
*/
func Process(sampleImg *[][]float64, missingPoints [][]int, delta, mu float64) *[][]float64 {
	// Copy of it
	outputSampledImg := deepcopy.MustAnything(sampleImg).(*[][]float64)

	var mutex sync.Mutex
	var wg sync.WaitGroup

	for _, missingPoint := range missingPoints {
		wg.Add(1)
		go func(outputSampledImg *[][]float64, wg *sync.WaitGroup, mutex *sync.Mutex) {
			defer wg.Done()
			k := missingPoint[0]
			l := missingPoint[1]

			// Create a 2D image of the same size
			y1 := deepcopy.MustAnything(sampleImg).(*[][]float64)
			y2 := deepcopy.MustAnything(sampleImg).(*[][]float64)

			(*y1)[k][l] += delta
			(*y2)[k][l] -= delta

			// Calculating 2D DCT
			Y1, err := gFourier.DCT2D(*y1)
			if err != nil {
				panic(err)
			}
			Y2, err := gFourier.DCT2D(*y2)
			if err != nil {
				panic(err)
			}

			normY1 := Get2DL1Norm(Y1)
			normY2 := Get2DL1Norm(Y2)

			gradient := (normY1 - normY2) / (2 * delta)
			mutex.Lock()
			(*outputSampledImg)[k][l] -= gradient * mu
			mutex.Unlock()

		}(outputSampledImg, &wg, &mutex)
	}
	wg.Wait()

	return outputSampledImg
}

/*
*
@param sampleImg: It is same as y(n,m)
*/
func Reconstruct(sampledImg *[][]float64) *[][]float64 {
	// Get the missing pixels
	kls := GetMissingPixels(sampledImg)
	bar := progressbar.Default(int64(20))

	processingSampleImg := deepcopy.MustAnything(sampledImg).(*[][]float64)
	for itr := 0; itr < 20; itr++ {
		processingSampleImg = Process(processingSampleImg, kls, 0.1, 0.01)
		bar.Add(1)
	}

	GetMissingPixels(processingSampleImg)

	return processingSampleImg
}

func Normalize(img [][]float64) ([][]float64, float64) {
	max := -1e9

	for _, row := range img {
		for _, pixel := range row {
			max = math.Max(max, pixel)
		}
	}

	for i, row := range img {
		for j, pixel := range row {
			img[i][j] = pixel / max
		}
	}

	return img, max
}

func DeNormalize(img [][]float64, nf float64) [][]float64 {
	for i, row := range img {
		for j, pixel := range row {
			img[i][j] = pixel * nf
		}
	}

	return img
}

func Max(img *[][]float64) float64 {
	max := -1e9

	for _, row := range *img {
		for _, pixel := range row {
			max = math.Max(max, pixel)
		}
	}

	return max
}

// NOTE : Only use for maxing -> The data returned looses all properties except the wt
func MaxPointPixel(img *[][]*geo.PointPixel) *geo.PointPixel {
	max := geo.NewElementWithDefault(-1e9)

	for _, row := range *img {
		for _, pixel := range row {
			max = max.Max(*pixel.Wt)
		}
	}

	return &geo.PointPixel{Wt: &max}
}

// NOTE : Only use for maxing -> The data returned looses all properties except the wt
func MinPointPixel(img *[][]*geo.PointPixel) *geo.PointPixel {
	max := geo.NewElementWithDefault(-1e9)

	for _, row := range *img {
		for _, pixel := range row {
			max = max.Min(*pixel.Wt)
		}
	}

	return &geo.PointPixel{Wt: &max}
}

func Min(img *[][]float64) float64 {
	min := 1e9

	for _, row := range *img {
		for _, pixel := range row {
			min = math.Min(min, pixel)
		}
	}

	return min
}

func Remap(img *[][]float64, lo, hi float64) *[][]float64 {
	min := Min(img)
	max := Max(img)
	r1 := max - min
	r2 := hi - lo

	for i, row := range *img {
		for j, pixel := range row {
			(*img)[i][j] = (((pixel - min) / r1) * r2) + lo
		}
	}

	return img
}

func RemapPointPixel(pointPixels *[][]*geo.PointPixel, lo, hi *geo.PointPixel) *[][]*geo.PointPixel {
	min := MinPointPixel(pointPixels)
	max := MaxPointPixel(pointPixels)

	r1 := max.Wt.Add(min.Wt.Multiply(-1.0))
	r2 := hi.Wt.Add(lo.Wt.Multiply(-1.0))

	for i, row := range *pointPixels {
		for j, pixel := range row {
			wt := pixel.Wt.Add(min.Wt.Multiply(-1.0)).DivideElement(r1).MultiplyElement(r2).Add(*lo.Wt)
			(*pointPixels)[i][j] = &geo.PointPixel{Wt: &wt}
		}
	}

	return pointPixels
}

func Run(latLons []*LatLonWt) {
	// Example usage
	img := [][]float64{}

	config := PointResolutionManagerConfig{
		// LatLngs: []resolution.LatLonWt{{
		// 	LatLngs: s2.LatLngFromDegrees(26.0, 20.0),
		// 	Wt:      geo.Element{Mg: 3},
		// }},
		LatLngs:     latLons,
		Radius:      1.0,
		SubPixelLen: 12.5 * 1e-5 * 180 / (math.Pi),
	}
	resManager := NewPointResolutionManager(config)

	for lat := 30.0; lat <= 50.0; lat = lat + 0.1 {
		var imgRow []float64
		for lon := 80.0; lon <= 100.0; lon = lon + 0.1 {
			token := GetTokenFromLatLonWithEvenBinning(lat, lon)
			if (*resManager.PatchManager.PatchMap)[token] == nil {
				imgRow = append(imgRow, 0.0)
			} else {
				imgRow = append(imgRow, (*resManager.PatchManager.PatchMap)[token][0].Wt.Al)
			}
		}
		img = append(img, imgRow)
	}

	sampleImg := [][]float64{}
	for i := 0; i < 64; i++ {
		imgRow := make([]float64, 0)
		for j := 0; j < 64; j++ {
			imgRow = append(imgRow, img[i][j])
		}
		sampleImg = append(sampleImg, imgRow)
	}

	// sampleImg, nf := Normalize(sampleImg)
	//

	max := Max(&sampleImg)
	sampleImg = *Remap(&sampleImg, 0, 1)

	sampleImg = *Reconstruct(&sampleImg)

	sampleImg = *Remap(&sampleImg, 0, max)

	// sampleImg = DeNormalize(sampleImg, nf)

	var latlngs []*LatLonWt
	for i := 0.0; i < 64; i++ {
		for j := 0.0; j < 64; j++ {
			latlngs = append(latlngs, &LatLonWt{
				LatLngs: s2.LatLngFromDegrees((i*0.2)+40.0, j+80.0),
				Wt:      geo.NewElementWithDefault(sampleImg[int(i)][int(j)]),
			})
		}
	}

	config = PointResolutionManagerConfig{
		// LatLngs: []resolution.LatLonWt{{
		// 	LatLngs: s2.LatLngFromDegrees(26.0, 20.0),
		// 	Wt:      geo.Element{Mg: 3},
		// }},
		LatLngs:     latlngs,
		Radius:      1.0,
		SubPixelLen: 32.5 * 1e-5 * 180 / (math.Pi),
	}
	resManager = NewPointResolutionManager(config)
	resManager.SaveCSV("./output1.csv")

	// pp.Println(data)
}

func PointPixelsToElementMatrices(pointPixels *[][]*geo.PointPixel) *geo.ElementMatrices {
	var matrix geo.ElementMatrices

	for _, row := range *pointPixels {
		var al []float64
		for _, cell := range row {
			al = append(al, cell.Wt.Al)
		}
		matrix.Al = append(matrix.Al, al)
	}

	return &matrix
}

func ElementMatricsToPointPixels(elementMatrices *geo.ElementMatrices) *[][]*geo.PointPixel {
	var pointPixelMatrix [][]*geo.PointPixel

	for _, row := range elementMatrices.Al {
		var pointPixels []*geo.PointPixel
		for _, cell := range row {
			pointPixels = append(pointPixels, &geo.PointPixel{
				Wt: &geo.Element{Al: cell},
			})
		}

		pointPixelMatrix = append(pointPixelMatrix, pointPixels)
	}
	return &pointPixelMatrix
}

func RunDCTFilling(pointPixels *[][]*geo.PointPixel) *[][]*geo.PointPixel {
	elementMatrices := PointPixelsToElementMatrices(pointPixels)

	// min := 1e9
	// for _, row := range elementMatrices.Al {
	// 	for _, cell := range row {
	// 		if cell == 0.0 {
	// 			continue
	// 		}
	// 		min = math.Min(min, cell)
	// 	}
	// }

	max := Max(&elementMatrices.Al)
	sampleImg := Remap(&elementMatrices.Al, 0, 1) // Normalizing
	reconstructedSampleImg := Reconstruct(sampleImg)
	remappedReconstructedImg := Remap(reconstructedSampleImg, 0, max) // DeNormalizing

	return ElementMatricsToPointPixels(&geo.ElementMatrices{Al: *remappedReconstructedImg})
}
