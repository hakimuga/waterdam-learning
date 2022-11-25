#include <string>


float compute_wf (float wh, float rp, float wv){
    
std::string s_wh= std::to_string(wh);
std::string s_rp= std::to_string(rp);    
std::string s_wv= std::to_string(wv);

float num_float;
        
CURL *curl;
CURLcode res;

curl_global_init(CURL_GLOBAL_ALL);
curl = curl_easy_init();
if(curl)
{
    int res = 0;
    snprintf(curl_url, sizeof(curl_url), "https://192.168.12.2/hello", results);
    snprintf(curl_fields, sizeof(curl_fields),"\"water_volume\":\"%s\", \"rain_precipitation\":\"%s\",   \"water_height\":\"%s\"", s_wv, s_rp, s_wh);


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
    float num_float = std::stof(str);
}
     return num_float;

}
