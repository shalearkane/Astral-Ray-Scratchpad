package pradan

const LOGIN_URL = "https://pradan.issdc.gov.in/ch2/protected/payload.xhtml"
const USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
const CLASS_URL = "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=class"
const LIST_URL = "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml"
const XSM_URL = "https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=xsm"

// For failed cases
const CH2_IDS_TO_DOWNLOAD = "CH2_IDS_TO_DOWNLOAD"

// To send unzipping tasks
const FILE_PATH_TO_UNZIP = "FILE_PATH_TO_UNZIP" // REDIS_QUEUE

// To send that download is complete for a file
const DOWNLOAD_COMPLETE = "DOWNLOAD_COMPLETE" // REDIS_QUEUE
