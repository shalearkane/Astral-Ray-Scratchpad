package resolution

import (
	"log/slog"
	"sr/geo"
	"sync"

	"github.com/k0kubun/pp/v3"
	"github.com/schollz/progressbar/v3"
)

func chunkBy[T any](items []T, chunkSize int) (chunks [][]T) {
	for chunkSize < len(items) {
		items, chunks = items[chunkSize:], append(chunks, items[0:chunkSize:chunkSize])
	}
	return append(chunks, items)
}

func (rm *PixelResolutionManager) EnhancePixels() error {
	var wg sync.WaitGroup
	var mutex sync.Mutex

	enhancedPixels := []geo.RectPixel{}

	for _, pixel := range rm.Pixels {
		wg.Add(1)
		go rm.enhancePixel(&pixel, &enhancedPixels, &mutex, &wg)
	}

	wg.Wait()
	rm.Pixels = enhancedPixels
	return nil
}

func (rm *PixelResolutionManager) enhancePixel(
	pixel *geo.RectPixel,
	enhancedPixels *[]geo.RectPixel,
	mutex *sync.Mutex,
	wg *sync.WaitGroup,
) {
	defer wg.Done()

	totalArea := pixel.BoundingBox.Area()
	wt := pixel.Wt.Multiply(totalArea)

	for _, p := range rm.Pixels {
		if p.ID == pixel.ID || !pixel.BoundingBox.Intersects(*p.BoundingBox) {
			continue
		}

		area := pixel.BoundingBox.Intersection(*p.BoundingBox).Area()
		if area > 0.0 {
			totalArea += area
			wt = wt.Add(p.Wt.Multiply(area))
		}
	}

	wt = wt.Divide(totalArea)
	newPixel := geo.RectPixel{
		BoundingBox: pixel.BoundingBox,
		Wt:          wt,
		ID:          pixel.ID,
	}

	mutex.Lock()
	*enhancedPixels = append(*enhancedPixels, newPixel)
	mutex.Unlock()
}

func (rm *PointResolutionManager) EnhanceAdditionalPixels(emptyPixelMap *map[string]*geo.PointPixel) {
	var wg sync.WaitGroup
	var mutex sync.Mutex
	slog.Info("--FILLING--")

	emptyPixels := make([]*geo.PointPixel, 0)
	for _, pixel := range *emptyPixelMap {
		emptyPixels = append(emptyPixels, pixel)
	}

	enhancedPixels := []*geo.PointPixel{}
	bar := progressbar.Default(int64(len(emptyPixels)))

	for _, pixelChunck := range chunkBy(emptyPixels, 1000) {
		for _, pixel := range pixelChunck {
			wg.Add(1)
			go rm.enhancePixel(pixel, &enhancedPixels, &mutex, &wg, bar, true)
		}
		wg.Wait()
	}

	for _, emptyPixel := range enhancedPixels {
		delete(*emptyPixelMap, emptyPixel.ID)
	}

	// Update the Resolution Manager
	*rm.PointPixels = append(*rm.PointPixels, enhancedPixels...)
	rm.PatchManager.ComputePatches(enhancedPixels)
	pp.Println(len(*rm.PointPixels))
}

func (rm *PointResolutionManager) EnhancePixels() {
	var wg sync.WaitGroup
	var mutex sync.Mutex

	enhancedPixels := []*geo.PointPixel{}
	slog.Info("--ENHANCING--")
	bar := progressbar.Default(int64(len(*rm.PointPixels)))

	for _, pixelChunck := range chunkBy(*rm.PointPixels, 1000) {
		for _, pixel := range pixelChunck {
			wg.Add(1)
			go rm.enhancePixel(pixel, &enhancedPixels, &mutex, &wg, bar, false)
		}
		wg.Wait()
	}

	*rm.PointPixels = enhancedPixels
}

func (rm *PointResolutionManager) enhancePixel(
	pixel *geo.PointPixel,
	enhancedPixels *[]*geo.PointPixel,
	mutex *sync.Mutex,
	wg *sync.WaitGroup,
	bar *progressbar.ProgressBar,
	interpolate bool,
) {
	defer wg.Done()
	pixelPolyon := pixel.BoundingBox.ToPolygon()
	totalArea := pixelPolyon.Area()
	wt := pixel.Wt.Multiply(totalArea)

	// Dont consider the pixel value if it has to be interpolated
	if interpolate {
		totalArea = 0
		wt = geo.NewElementWithDefault(0.0)
	}

	for _, p := range rm.PatchManager.Search(pixel) {
		if p.ID == pixel.ID {
			continue
		}

		area := geo.GetPolygonAreaOfIntersection(pixelPolyon, p.BoundingBox.ToPolygon())

		if area > 0.00005 || (interpolate && area > 0) {
			totalArea += area
			wt = wt.Add(p.Wt.Multiply(area))
		}
	}

	wt = wt.Divide(totalArea)

	if (interpolate && totalArea > 0) || !interpolate {
		mutex.Lock()
		*enhancedPixels = append(*enhancedPixels, &geo.PointPixel{
			BoundingBox: pixel.BoundingBox,
			Wt:          &wt,
			ID:          pixel.ID,
			Center:      pixel.Center,
		})
		mutex.Unlock()
	}
	bar.Add(1)
}
