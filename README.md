# Downloading-Documents
This script is designed to fetch and download documents from the USPTO (United States Patent and Trademark Office) TTAB Reading Room.

**Overview**
    1. Purpose:
        The script interacts with the USPTO's TTAB Reading Room API to retrieve document metadata and download PDF documents corresponding to specific cases.
    2. Workflow:
        Fetches metadata about documents via an API.
        Extracts document links and proceeding numbers from the API response.
        Downloads each document as a PDF file and saves it locally.
**Implementation Details**
    1. download_with_retries function
        Handles the retry mechanism for downloading files.
        Implements exponential backoff to prevent overwhelming the server during retries:
            Wait time doubles with each retry (up to a maximum of max_delay).
            Adds random variation to avoid repeated retries from multiple clients at the same time.
        Inputs:
            url: URL of the document to download.
            num: Identifier (proceeding number) of the document.
            retries, delay, and max_delay: Control the retry behavior.
        Output:
            Saves the document as num.pdf in the working directory if successful.
            Prints failure after exhausting retries.
    2. get_documents function
        Interacts with the USPTO API to fetch metadata for documents.
        Constructs document links and extracts proceeding numbers from the API response.
        Steps:
            Sends a GET request to fetch session cookies.
            Sends a POST request with the search payload to retrieve document metadata.
            Parses JSON response to build:
                A list of document URLs.
                A list of corresponding proceeding numbers.
        Output:
            A dictionary containing documentLinks (URLs) and proceedingNumber (case IDs).
    3. download_documents function
        Coordinates the overall process.
        Creates a directory TTAB Cases in the current working directory to store downloaded files.
        Uses FuturesSession from the requests_futures library for concurrent downloads.
        Handles retry logic if a document fails to download on the first attempt.
        Steps:
            Calls get_documents to retrieve document URLs and proceeding numbers.
            Initiates asynchronous downloads for all documents.
            Writes the downloaded content to a file in the designated directory.
        Output:
            Saves each document as <proceeding_number>.pdf in the TTAB Cases folder.
**Key Libraries Used**
    requests: For handling HTTP GET and POST requests.
    requests_futures: For asynchronous requests, enabling concurrent downloads.
    os: To manage directories and file paths.
    json: For parsing API responses.
    time & random: For implementing retry delays with random variations.
    concurrent.futures: To process multiple downloads concurrently.
**Execution Flow**
    1. The script calls download_documents() directly, starting the process.
    2. download_documents:
        Fetches document metadata via get_documents.
        Prepares a directory for storing files.
        Initiates asynchronous downloads.
    3. If any download fails, the download_with_retries function is invoked to attempt re-downloading with retries.



