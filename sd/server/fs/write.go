package fs

import (
	"encoding/base64"
	"os"
)

func WriteBase64(base64String, filePath string) {
	dec, err := base64.StdEncoding.DecodeString(base64String)
	if err != nil {
		panic(err)
	}

	f, err := os.Create(filePath)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	if _, err := f.Write(dec); err != nil {
		panic(err)
	}
	if err := f.Sync(); err != nil {
		panic(err)
	}
}
