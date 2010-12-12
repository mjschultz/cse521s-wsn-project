/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
/*
 * curl.h
 * Copyright (C) Matt Lindsay 2010 <matthew.scott.lindsay@gmail.com>
 *
 * CSE521S project
 * Gateway is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 * 
 */

#ifndef _Curl_H_
#define _Curl_H_

#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <string.h>
  
#include <curl/curl.h>

typedef unsigned long long UINT64;
typedef unsigned int UINT32;
typedef unsigned short UINT16;
typedef unsigned char UINT8;

class Curl
{
private:

	struct MemoryStruct
	{
		char *memory;
		size_t size;
	};
	
	struct AddMeter
	{
		int status;
		int id;
	} meter;
	
public:
	Curl();
	~Curl();

	void setURL(char* setURL);
	char* getURL();
	int getStatus();
	void putStatus(int setStatus);
	int getID();
	void putID(int setID);
	static size_t put_callback(void *ptr, size_t size, size_t nmemb, void *userp);
	static void *myrealloc(void *ptr, size_t size);
	static size_t write_data(void *ptr, size_t size, size_t nmemb, void *data);
	int putSpace(int spaceID, int is_empty, int light, int temp);
	
protected:
	char *url;	
};

#endif // _Curl_H_
