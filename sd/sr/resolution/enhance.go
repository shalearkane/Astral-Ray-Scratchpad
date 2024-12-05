package resolution

import (
	"sr/geo"
	"sync"

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

func (rm *PointResolutionManager) EnhancePixels() error {
	var wg sync.WaitGroup
	var mutex sync.Mutex

	enhancedPixels := []*geo.PointPixel{}
	bar := progressbar.Default(int64(len(*rm.PointPixels)))

	for _, pixelChunck := range chunkBy(*rm.PointPixels, 1000) {
		for _, pixel := range pixelChunck {
			wg.Add(1)
			go rm.enhancePixel(pixel, &enhancedPixels, &mutex, &wg, bar)
		}
		wg.Wait()
	}

	*rm.PointPixels = enhancedPixels
	return nil
}

func (rm *PointResolutionManager) enhancePixel(
	pixel *geo.PointPixel,
	enhancedPixels *[]*geo.PointPixel,
	mutex *sync.Mutex,
	wg *sync.WaitGroup,
	bar *progressbar.ProgressBar,
) {
	defer wg.Done()

	totalArea := pixel.BoundingBox.Area()
	wt := pixel.Wt.Multiply(totalArea)

	for _, p := range rm.PatchManager.Search(pixel) {
		if p.ID == pixel.ID {
			continue
		}

		area := geo.GetPolygonAreaOfIntersection(pixel.BoundingBox, p.BoundingBox)

		if area > 0.00005 {
			totalArea += area
			wt = wt.Add(p.Wt.Multiply(area))
		}
	}

	wt = wt.Divide(totalArea)

	mutex.Lock()
	*enhancedPixels = append(*enhancedPixels, &geo.PointPixel{
		BoundingBox: pixel.BoundingBox,
		Wt:          wt,
		ID:          pixel.ID,
	})
	mutex.Unlock()
	bar.Add(1)
}
