/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
/*
 * curl.cpp
 * Copyright (C) Matt Lindsay 2010 <matthew.scott.lindsay@gmail.com>
 *
 * CSE521S project
 * Gateway is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 *
 */

#include "json.h"
#include "curl.h"

Curl::Curl()
{
	
}

Curl::~Curl()
{
	
}

void Curl::setURL(char* setURL)
{
	url = setURL;
}

char* Curl::getURL()
{
	return url;
}

int Curl::getStatus()
{
	return meter.status;
}

void Curl::putStatus(int setStatus)
{
	meter.status = setStatus;
}

int Curl::getID()
{
	return meter.id;
}

void Curl::putID(int setID)
{
	meter.id = setID;
}

size_t Curl::put_callback(void *ptr, size_t size, size_t nmemb, void *userp) 
{
	struct MemoryStruct *data = (struct MemoryStruct *)userp;

	if(size*nmemb < 1)
	{	
		return 0;
	}

	if(data->size)
	{
		*(char *)ptr = data->memory[0];
		data->memory++;
		data->size--;

		return 1;
	}
	
	return 0;
}

void *Curl::myrealloc(void *ptr, size_t size)
{
	if(ptr)
	{
		return realloc(ptr, size);
	}
	else
	{
		return malloc(size);
	}
}

size_t Curl::write_data(void *ptr, size_t size, size_t nmemb, void *data)
{
	size_t realsize = size * nmemb;
	struct MemoryStruct *mem = (struct MemoryStruct *)data;
 
	mem->memory = (char*)myrealloc(mem->memory, mem->size + realsize + 1);
	if (mem->memory)
	{
		memcpy(&(mem->memory[mem->size]), ptr, realsize);
		mem->size += realsize;
		mem->memory[mem->size] = 0;
	}
	return realsize;
}

int Curl::putSpace(int spaceID, int is_empty, int light, int temp)
{
	CURL *curl;
	CURLcode res; 
	
	struct MemoryStruct data;
	struct MemoryStruct chunk;
	struct curl_slist *headers = NULL;
	
	char payload[200];
	
	if(is_empty  ==  0)
	{
		sprintf(payload,"[{\"space_id\" : %d,\"is_empty\" : true,\"light\" : %d,\"temperature\" : %d}]",spaceID, light, temp);
	}
	else
	{
		sprintf(payload,"[{\"space_id\" : %d,\"is_empty\" : false,\"light\" : %d,\"temperature\" : %d}]",spaceID, light, temp);
	}
	
	data.memory = payload;
	data.size = strlen(payload);
	
	chunk.memory=NULL;
	chunk.size = 0;
	
	curl_global_init(CURL_GLOBAL_ALL);
 
	curl = curl_easy_init();
	
	if(curl)
	{	  
		headers = curl_slist_append(headers, "Content-Type: application/x-www-form-urlencoded");
	  
		curl_easy_setopt( curl, CURLOPT_HTTPHEADER, headers);
		curl_easy_setopt( curl, CURLOPT_URL, "cse521s-wsn-project.appspot.com/lot/wustl_millbrook/");
		curl_easy_setopt( curl, CURLOPT_WRITEFUNCTION, &write_data);
		curl_easy_setopt( curl, CURLOPT_WRITEDATA, (void *)&chunk);
		//curl_easy_setopt( curl, CURLOPT_VERBOSE, 1);
		curl_easy_setopt( curl, CURLOPT_HEADER, 1);
		curl_easy_setopt( curl, CURLOPT_READFUNCTION, put_callback);
		curl_easy_setopt( curl, CURLOPT_READDATA, &data); // This is what READFUNCTION uses to determine length
		curl_easy_setopt( curl, CURLOPT_UPLOAD, 1);
		curl_easy_setopt( curl, CURLOPT_PUT, 1);
		curl_easy_setopt( curl, CURLOPT_INFILESIZE, strlen(payload));  // Used for Content-Length

		res = curl_easy_perform(curl);

		curl_easy_cleanup(curl);
	}

//	fprintf(stderr,"%s\n",chunk.memory); 
	
	if(chunk.memory)
	{
		free(chunk.memory);
	}

	curl_global_cleanup();

	return 0;
}