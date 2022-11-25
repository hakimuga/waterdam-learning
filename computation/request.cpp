
float compute_wf (float parameter1, float parameter2, float parameter3)
CURL *curl;
CURLcode res;

curl_global_init(CURL_GLOBAL_ALL);
curl = curl_easy_init();
if(curl)
{
    int res = 0;
    snprintf(curl_url, sizeof(curl_url), "https://%s:8080/hello", results);
    snprintf(curl_fields, sizeof(curl_fields),"\"water_volume\":\"%s\", \"rain_precipitation\":\"%s\",   \"water_height\":\"%s\"", water_volume, rain_precipitation, water_height);


    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Accept: application/json");
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "charset: utf-8");

    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_URL, curl_url);
    curl_easy_setopt(curl, CURLOPT_POST, 1);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, curl_fields);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
  
    res = curl_easy_perform(curl);
    std::cout << readBuffer << std::endl;



    curl_easy_cleanup(curl);
    curl_global_cleanup();
  
}

}
