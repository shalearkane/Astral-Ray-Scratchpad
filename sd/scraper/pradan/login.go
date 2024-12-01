package pradan

import (
	"log/slog"
	"os"
	"time"

	"github.com/anaskhan96/soup"
	"github.com/go-resty/resty/v2"
)

func Login() (*string, error) {
	slog.Info("Logging in to Pradan")
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
