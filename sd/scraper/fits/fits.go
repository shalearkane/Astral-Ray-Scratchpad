package fits

import (
	"os"

	fits "github.com/astrogo/fitsio"
	"github.com/k0kubun/pp/v3"
)

func ExtractFITSData(filePath string) {
	r, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer r.Close()
	f, err := fits.Open(r)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	// get the second HDU
	table := f.HDU(1).(*fits.Table)
	nrows := table.NumRows()
	rows, err := table.Read(0, nrows)
	if err != nil {
		panic(err)
	}
	pp.Println(rows)
	defer rows.Close()

}
