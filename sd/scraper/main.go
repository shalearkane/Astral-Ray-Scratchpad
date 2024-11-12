package main

import (
	"fmt"
	"os"
	"scraper/fits"
	"time"

	"github.com/anaskhan96/soup"
	"github.com/go-resty/resty/v2"
	"github.com/go-rod/rod"
	"github.com/joho/godotenv"
	"github.com/k0kubun/pp/v3"
)

const LOGIN_URL = "https://pradan.issdc.gov.in/ch2/protected/payload.xhtml"
const USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
const CLASS_URL = "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=class"
const LIST_URL = "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml"

func logout(page *rod.Page) {
	fmt.Println(" ---> Logging out...")
	logout_script := `
		document.getElementById("j_idt30").children[1].children[0].children[1].children[1].children[0].click()
	`
	page.Eval(logout_script)
	page.MustWaitStable()
	fmt.Println(" ---> Logging out successful")
}

func goToCLASSPage(page *rod.Page) {
	fmt.Println(" ---> Going to CLASS page...")
	page.Navigate("https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=class")
	page.MustWaitStable()
	fmt.Println(" ---> Going to CLASS page successful")
}

func login(page *rod.Page) {
	fmt.Println(" ---> Logging in...")
	page.MustElement("#username").MustInput(os.Getenv("USERNAME"))
	fmt.Println(os.Getenv("USERNAME"))
	fmt.Println(os.Getenv("PASSWORD"))
	page.MustElement("#password").MustInput(os.Getenv("PASSWORD"))
	page.MustElement("#kc-login").MustClick()
	fmt.Println(" ---> Logging in successful")

}

func LoginToPradan() (*string, error) {
	pp.Println("-----> Logging in to Pradan")
	client := resty.New()
	// Get the login page to get the cookies
	loginPage, err := client.SetTimeout(5*time.Second).SetRetryCount(20).R().EnableTrace().SetHeader("User-Agent", USER_AGENT).Get(LOGIN_URL)
	if err != nil {
		return nil, err
	}

	// Get all the SET-COOKIE headers
	cookies := ""
	for _, cookie := range loginPage.Cookies() {
		cookies += cookie.Raw + ";"
	}

	loginPostURL := soup.HTMLParse(string(loginPage.Body())).Find("form").Attrs()["action"]

	// Login to pradan
	loginResponse, err := client.SetTimeout(5*time.Minute).SetRetryCount(20).R().EnableTrace().SetHeader("User-Agent", USER_AGENT).SetFormData(map[string]string{
		"username":     os.Getenv("USERNAME"),
		"password":     os.Getenv("PASSWORD"),
		"credentialId": "",
	}).Post(loginPostURL)
	if err != nil {
		return nil, err
	}

	cookies = cookies + loginResponse.RawResponse.Request.Header.Get("Cookie")

	return &cookies, nil
}

func GetDataList(cookies string) error {
	pp.Println("-----> Extracting data list")

	client := resty.New()
	entriesToRetrieve := 100

	list, err := client.SetTimeout(5*time.Minute).SetRetryCount(20).R().EnableTrace().SetHeader("User-Agent", USER_AGENT).SetHeader("Cookie", cookies).SetFormData(map[string]string{
		"javax.faces.partial.ajax": "true", "javax.faces.source": "tableForm:lazyDocTable", "javax.faces.partial.execute": "tableForm:lazyDocTable", "javax.faces.partial.render": "tableForm:lazyDocTable", "tableForm:lazyDocTable": "tableForm:lazyDocTable", "tableForm:lazyDocTable_pagination": "true", "tableForm:lazyDocTable_first": "0", "tableForm:lazyDocTable_rows": string(entriesToRetrieve), "tableForm:lazyDocTable_skipChildren": "true", "tableForm:lazyDocTable_encodeFeature": "true", "tableForm": "tableForm", "tableForm:lazyDocTable_rppDD": string(entriesToRetrieve), "tableForm:lazyDocTable_selection": "", "tableForm:docDetail_scrollState": "0,0", "tableForm:colSelectList_source": "MD5Sum;STRING;label.Product_Observational.File_Area_Observational.File.md5_checksum", "tableForm:colSelectList_target": "Filename;STRING;filename", "javax.faces.ViewState": "1183150074830565578:-7765262062444575069",
	}).SetFormData(map[string]string{
		"tableForm:colSelectList_source": "CreationTime;TIME;label.Product_Observational.File_Area_Observational.File.creation_date_time",
		"tableForm:colSelectList_target": "StartTime;TIME;label.Product_Observational.Observation_Area.Time_Coordinates.start_date_time",
	}).SetFormData(map[string]string{
		"tableForm:colSelectList_target": "EndTime;TIME;label.Product_Observational.Observation_Area.Time_Coordinates.stop_date_time",
	}).SetFormData(map[string]string{
		"tableForm:colSelectList_target": "FileSizeInBytes;INTEGER;label.Product_Observational.File_Area_Observational.File.file_size.content",
	}).Post(LIST_URL)

	if err != nil {
		panic(err)
	}

	pp.Println(string(list.Body()))

	return nil
}

func main() {
	// pp.Default.SetColoringEnabled(false)
	// Load the .env file
	godotenv.Load()

	// page := rod.New().MustConnect().MustPage("https://pradan.issdc.gov.in/ch2/protected/payload.xhtml")
	// defer page.Close()

	// login(page)

	// goToCLASSPage(page)

	// page.MustScreenshot("a.png")

	// logout(page)
	// page.MustWaitStable().MustScreenshot("b.png")

	// cookies, err := LoginToPradan()
	// if err == nil {
	// 	GetDataList(*cookies)
	// }

	fits.ExtractFITSData("./test.fits")

}
