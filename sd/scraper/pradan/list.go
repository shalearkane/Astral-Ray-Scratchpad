package pradan

import (
	"log/slog"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/anaskhan96/soup"
	"github.com/go-resty/resty/v2"
)

func (pradan *PradanClient) GetClassViewState(resultantViewState *string, wg *sync.WaitGroup) (*string, error) {
	defer wg.Done()
	slog.Info("Preparing to get CLASS viewState")
	client := resty.New()

	pageFormData := map[string]string{
		"filterForm":                               "filterForm",
		"filterForm:j_idt53":                       "VIEW",
		"filterForm:filterTable:0:attr":            "ObservationTime;TIME_DURATION;label.Product_Observational.Observation_Area.Time_Coordinates.start_date_time, label.Product_Observational.Observation_Area.Time_Coordinates.stop_date_time",
		"filterForm:filterTable:0:opr":             "TIME_DURATION,TimeDurationIn",
		"filterForm:filterTable:0:datetime1_input": pradan.ClassTimeStart,
		"filterForm:filterTable:0:datetime2_input": pradan.ClassTimeEnd,
		"filterForm:filterButton":                  "Filter",
	}
	pageClient := client.SetTimeout(6 * time.Minute).SetRetryCount(20).R().EnableTrace().SetHeaders(map[string]string{
		"Cookie":     pradan.Cookies,
		"User-Agent": USER_AGENT,
		"Origin":     "https://pradan.issdc.gov.in",
		"Referer":    "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=class",
	}).SetFormData(pageFormData)

	// In order to get timestamp filters working we need to get the ViewState. A viewState can be received from the backend from the initial call of the page.
	// This is a state which is managed by the backend itself. So what we need to do is simulate actions with this viewState and call backend for the list.
	page, err := pageClient.Post(LIST_URL)
	if err != nil {
		return nil, err
	}

	viewState := soup.HTMLParse(string(page.Body())).Find("input", "name", "javax.faces.ViewState").Attrs()["value"]
	pageFormData["javax.faces.ViewState"] = viewState
	slog.Info("Achieved the CLASS viewState")
	slog.Info("Preparing to update the CLASS viewState")

	// Now as we have received the viewState we need to make modifications to our view in order to apply it
	// NOTE: This will take a long amount of time
	_, err = pageClient.SetFormData(pageFormData).Post(LIST_URL)
	if err != nil {
		return nil, err
	}

	slog.Info("Updated the CLASS viewState")

	*resultantViewState = viewState
	return &viewState, nil
}

func (pradan *PradanClient) GetXSMViewState(resultantViewState *string, wg *sync.WaitGroup) (*string, error) {
	defer wg.Done()
	slog.Info("Preparing to get XSM viewState")
	client := resty.New()

	pageFormData := map[string]string{
		"filterForm":                               "filterForm",
		"filterForm:j_idt53":                       "VIEW",
		"filterForm:filterTable:0:attr":            "ObservationDate;DATE_DURATION;label.Product_Observational.Observation_Area.Time_Coordinates.obs_date, label.Product_Observational.Observation_Area.Time_Coordinates.obs_date",
		"filterForm:filterTable:0:opr":             "DATE_DURATION,TimeDurationIn",
		"filterForm:filterTable:0:datetime1_input": pradan.XSMTimeStart,
		"filterForm:filterTable:0:datetime2_input": pradan.XSMTimeEnd,
		"filterForm:filterButton":                  "Filter",
	}
	pageClient := client.SetTimeout(6 * time.Minute).SetRetryCount(20).R().EnableTrace().SetHeaders(map[string]string{
		"Cookie":                    pradan.Cookies,
		"User-Agent":                USER_AGENT,
		"Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
		"Accept-Language":           "en-GB,en-US;q=0.9,en;q=0.8",
		"Cache-Control":             "max-age=0",
		"Connection":                "keep-alive",
		"Content-Type":              "application/x-www-form-urlencoded",
		"DNT":                       "1",
		"Origin":                    "https://pradan.issdc.gov.in",
		"Referer":                   "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=xsm",
		"Sec-Fetch-Dest":            "document",
		"Sec-Fetch-Mode":            "navigate",
		"Upgrade-Insecure-Requests": "1",
	}).SetFormData(pageFormData)

	// In order to get timestamp filters working we need to get the ViewState. A viewState can be received from the backend from the initial call of the page.
	// This is a state which is managed by the backend itself. So what we need to do is simulate actions with this viewState and call backend for the list.
	page, err := pageClient.Post(XSM_URL)
	if err != nil {
		return nil, err
	}

	viewState := soup.HTMLParse(string(page.Body())).Find("input", "name", "javax.faces.ViewState").Attrs()["value"]
	pageFormData["javax.faces.ViewState"] = viewState
	slog.Info("Achieved the XSM viewState")
	slog.Info("Preparing to update the XSM viewState")

	// Now as we have received the viewState we need to make modifications to our view in order to apply it
	// NOTE: This will take a long amount of time
	_, err = pageClient.SetFormData(pageFormData).SetBody(`filterForm=filterForm&filterForm%3Aj_idt53=VIEW&filterForm%3AfilterTable%3A0%3Aattr=ObservationTime%3BTIME_DURATION%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.start_date_time%2C+label.Product_Observational.Observation_Area.Time_Coordinates.stop_date_time&filterForm%3AfilterTable%3A0%3Aopr=TIME_DURATION%2CTimeDurationIn&filterForm%3AfilterTable%3A0%3Adatetime1_input=2022-11-03+00%3A00%3A00&filterForm%3AfilterTable%3A0%3Adatetime2_input=2023-11-24+00%3A00%3A00&filterForm%3AfilterButton=Filter&javax.faces.ViewState=` + viewState).Post(XSM_URL)
	if err != nil {
		return nil, err
	}

	slog.Info("Updated the XSM viewState")
	*resultantViewState = viewState

	return &viewState, nil
}

func (pradan *PradanClient) GetCLASSDataList(channel chan []string) (*[]string, error) {
	client := resty.New()
	slog.Info("Preparing to fetch the lists")

	entriesToRetrieve := 1000
	pageNo := 0 // Starting from 0

	var fileIds []string

	// Loop all the pages untill we get the full list
	for true {

		slog.Info("Fetching Page: %d", pageNo)

		// Now call the lists again for the data
		// Pass the viewState to have the filter applied
		list, err := client.SetTimeout(5 * time.Minute).SetRetryCount(20).R().EnableTrace().SetHeaders(map[string]string{
			"Cookie":           pradan.Cookies,
			"User-Agent":       USER_AGENT,
			"Origin":           "https://pradan.issdc.gov.in",
			"Referer":          "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=class",
			"X-Requested-With": "XMLHttpRequest",
			"Accept":           "application/xml, text/xml, */*; q=0.01",
			"Connection":       "keep-alive",
			"Content-Type":     "application/x-www-form-urlencoded; charset=UTF-8",
		}).SetBody("javax.faces.partial.ajax=true&javax.faces.source=tableForm%3AlazyDocTable&javax.faces.partial.execute=tableForm%3AlazyDocTable&javax.faces.partial.render=tableForm%3AlazyDocTable&tableForm%3AlazyDocTable=tableForm%3AlazyDocTable&tableForm%3AlazyDocTable_pagination=true&tableForm%3AlazyDocTable_first=" + strconv.Itoa(pageNo*entriesToRetrieve) + "&tableForm%3AlazyDocTable_rows=" + strconv.Itoa(entriesToRetrieve) + "&tableForm%3AlazyDocTable_skipChildren=true&tableForm%3AlazyDocTable_encodeFeature=true&tableForm=tableForm&tableForm%3AlazyDocTable_rppDD=" + strconv.Itoa(entriesToRetrieve) + "&tableForm%3AlazyDocTable_selection=&tableForm%3AdocDetail_scrollState=0%2C0&tableForm%3AcolSelectList_source=MD5Sum%3BSTRING%3Blabel.Product_Observational.File_Area_Observational.File.md5_checksum&tableForm%3AcolSelectList_source=CreationTime%3BTIME%3Blabel.Product_Observational.File_Area_Observational.File.creation_date_time&tableForm%3AcolSelectList_target=Filename%3BSTRING%3Bfilename&tableForm%3AcolSelectList_target=StartTime%3BTIME%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.start_date_time&tableForm%3AcolSelectList_target=EndTime%3BTIME%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.stop_date_time&tableForm%3AcolSelectList_target=FileSizeInBytes%3BINTEGER%3Blabel.Product_Observational.File_Area_Observational.File.file_size.content&javax.faces.ViewState=" + pradan.ClassViewState).Post(LIST_URL)

		if err != nil {
			return nil, err
		}

		dataList := soup.HTMLParse(string(list.Body())).FindAll("a")
		var newFileIds []string

		for _, a := range dataList {
			href := a.Attrs()["href"]
			if strings.Contains(href, "downloadData") && !strings.Contains(href, "xml") {
				newFileIds = append(newFileIds, href)
			}
		}

		fileIds = append(fileIds, newFileIds...)
		(channel) <- newFileIds

		if len(newFileIds) < entriesToRetrieve {
			break
		}
		pageNo = pageNo + 1 // Get the next page
	}

	// Close the channel
	close(channel)

	return &fileIds, nil
}

func (pradan *PradanClient) GetXSMDataList(channel chan []string) (*[]string, error) {
	client := resty.New()
	slog.Info("Preparing to fetch the lists")

	entriesToRetrieve := 1000
	pageNo := 0 // Starting from 0

	var fileIds []string

	// Loop all the pages untill we get the full list
	for true {

		slog.Info("Fetching Page: %d", pageNo)

		// Now call the lists again for the data
		// Pass the viewState to have the filter applied
		list, err := client.SetTimeout(5 * time.Minute).SetRetryCount(20).R().EnableTrace().SetHeaders(map[string]string{
			"Cookie":           pradan.Cookies,
			"User-Agent":       USER_AGENT,
			"Origin":           "https://pradan.issdc.gov.in",
			"Referer":          "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=xsm",
			"X-Requested-With": "XMLHttpRequest",
			"Accept":           "application/xml, text/xml, */*; q=0.01",
			"Connection":       "keep-alive",
			"Content-Type":     "application/x-www-form-urlencoded; charset=UTF-8",
		}).SetBody("javax.faces.partial.ajax=true&javax.faces.source=tableForm%3AlazyDocTable&javax.faces.partial.execute=tableForm%3AlazyDocTable&javax.faces.partial.render=tableForm%3AlazyDocTable&tableForm%3AlazyDocTable=tableForm%3AlazyDocTable&tableForm%3AlazyDocTable_pagination=true&tableForm%3AlazyDocTable_first=" + strconv.Itoa(pageNo*entriesToRetrieve) + "&tableForm%3AlazyDocTable_rows=" + strconv.Itoa(entriesToRetrieve) + "&tableForm%3AlazyDocTable_skipChildren=true&tableForm%3AlazyDocTable_encodeFeature=true&tableForm=tableForm&tableForm%3AlazyDocTable_rppDD=" + strconv.Itoa(entriesToRetrieve) + "&tableForm%3AlazyDocTable_selection=&tableForm%3AdocDetail_scrollState=0%2C0&tableForm%3AcolSelectList_source=StartTime%3BTIME%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.start_date_time&tableForm%3AcolSelectList_source=EndTime%3BTIME%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.stop_date_time&tableForm%3AcolSelectList_source=MD5Sum%3BSTRING%3Blabel.Product_Observational.File_Area_Observational.File.md5_checksum&tableForm%3AcolSelectList_source=CreationTime%3BTIME%3Blabel.Product_Observational.File_Area_Observational.File.creation_date_time&tableForm%3AcolSelectList_target=Filename%3BSTRING%3Bfilename&tableForm%3AcolSelectList_target=ObservationDate%3BDATE%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.obs_date&tableForm%3AcolSelectList_target=TotalExposure(s)%3BINTEGER%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.total_exposure&tableForm%3AcolSelectList_target=SunExposure(s)%3BINTEGER%3Blabel.Product_Observational.Observation_Area.Time_Coordinates.sun_exposure&tableForm%3AcolSelectList_target=FileSize(MB)%3BINTEGER%3Blabel.Product_Observational.File_Area_Observational.File.file_size.content&javax.faces.ViewState=" + pradan.XSMViewState).Post(XSM_URL)

		if err != nil {
			return nil, err
		}

		dataList := soup.HTMLParse(string(list.Body())).FindAll("a")
		var newFileIds []string

		for _, a := range dataList {
			href := a.Attrs()["href"]
			if strings.Contains(href, "downloadData") && !strings.Contains(href, "xml") {
				newFileIds = append(newFileIds, href)
			}
		}

		fileIds = append(fileIds, newFileIds...)
		(channel) <- newFileIds

		if len(newFileIds) < entriesToRetrieve {
			break
		}
		pageNo = pageNo + 1 // Get the next page
	}

	// Close the channel
	close(channel)

	return &fileIds, nil
}
