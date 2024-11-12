package main

import (
	"archive/zip"
	"fmt"
	"io"
	"log"
	"os"
	"strings"
	"sync"

	"github.com/google/uuid"
	cp "github.com/otiai10/copy"
)

func Extract(filePath string, fileIdx int, wg *sync.WaitGroup) {
	fileId := uuid.New().String()
	// defer wg.Done()

	fmt.Println()
	// Open a zip archive for reading.
	r, err := zip.OpenReader(filePath)
	if err != nil {
		log.Fatalf("impossible to open zip reader: %s", err)
	}
	defer r.Close()

	// Iterate through the files in the archive,
	for k, f := range r.File {

		// define the new file path
		newFilePath := fmt.Sprintf("uncompressed/%s/%s", fileId, f.Name)

		// CASE 1 : we have a directory
		if f.FileInfo().IsDir() {
			// if we have a directory we have to create it
			err = os.MkdirAll(newFilePath, 0777)
			if err != nil {
				log.Fatalf("impossible to MkdirAll: %s", err)
			}
			// we can go to next iteration
			continue
		}

		fmt.Printf("| ZIP %d | Unzipping %s:\n", fileIdx, f.Name)
		rc, err := f.Open()
		if err != nil {
			log.Fatalf("impossible to open file n°%d in archine: %s", k, err)
		}
		defer rc.Close()

		// CASE 2 : we have a file
		// create new uncompressed file
		uncompressedFile, err := os.Create(newFilePath)
		if err != nil {
			log.Fatalf("impossible to create uncompressed: %s", err)
		}
		_, err = io.Copy(uncompressedFile, rc)
		if err != nil {
			log.Fatalf("impossible to copy file n°%d: %s", k, err)
		}
	}

	entries, err := os.ReadDir(fmt.Sprintf("./uncompressed/%s/", fileId))
	if err != nil {
		log.Fatal(err)
	}

	var fileCopyWg sync.WaitGroup

	for _, e := range entries {
		fileCopyWg.Add(1)
		go func(wg *sync.WaitGroup) {
			cp.Copy(fmt.Sprintf("./uncompressed/%s/%s", fileId, e.Name()), "./data/merged", cp.Options{
				NumOfWorkers: 10,
			})
			wg.Done()

		}(&fileCopyWg)
	}

	// Save space and remove the uncompressed folder
	os.RemoveAll(fmt.Sprintf("./uncompressed/%s/", fileId))

	fileCopyWg.Wait()

}

func main() {
	var wg sync.WaitGroup

	entries, err := os.ReadDir("./files/")
	if err != nil {
		log.Fatal(err)
	}

	fileProcessIdx := 0

	for _, e := range entries {
		if len(strings.Split(e.Name(), ".")) > 1 && strings.Split(e.Name(), ".")[1] == "zip" {
			fileProcessIdx = fileProcessIdx + 1
			if fileProcessIdx > 2 {
				// wg.Add(1)
			 Extract(fmt.Sprintf("./files/%s", e.Name()), fileProcessIdx, &wg)
			}
		}
	}


}
