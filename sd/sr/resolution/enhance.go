package resolution

import (
	"sr/geo"
	"sync"

	"github.com/schollz/progressbar/v3"
)

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
		if p.ID == pixel.ID || !pixel.BoundingBox.Intersects(p.BoundingBox) {
			continue
		}

		area := pixel.BoundingBox.Intersection(p.BoundingBox).Area()
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

	enhancedPixels := []geo.PointPixel{}
	bar := progressbar.Default(int64(len(rm.PointPixels)))

	for _, pixel := range rm.PointPixels {
		wg.Add(1)
		go rm.enhancePixel(&pixel, &enhancedPixels, &mutex, &wg, bar)
	}

	wg.Wait()
	rm.PointPixels = enhancedPixels
	return nil
}

func (rm *PointResolutionManager) enhancePixel(
	pixel *geo.PointPixel,
	enhancedPixels *[]geo.PointPixel,
	mutex *sync.Mutex,
	wg *sync.WaitGroup,
	bar *progressbar.ProgressBar,
) {
	defer wg.Done()

	totalArea := pixel.BoundingBox.Area()
	wt := pixel.Wt.Multiply(totalArea)

	for _, p := range rm.PointPixels {
		if p.ID == pixel.ID {
			continue
		}

		area := geo.GetPolygonAreaOfIntersection(pixel.BoundingBox, p.BoundingBox)
		if area > 0.0 {
			totalArea += area
			wt = wt.Add(p.Wt.Multiply(area))
		}
	}

	wt = wt.Divide(totalArea)
	newPixel := geo.PointPixel{
		BoundingBox: pixel.BoundingBox,
		Wt:          wt,
		ID:          pixel.ID,
	}

	mutex.Lock()
	*enhancedPixels = append(*enhancedPixels, newPixel)
	mutex.Unlock()
	bar.Add(1)
}
