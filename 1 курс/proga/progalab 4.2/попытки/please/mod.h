#pragma once
#define Export __declspec(dllexport)

extern "C" {
	Export void* make();
	Export void clear(void* handle);
	Export void destroy(void* handle);

	Export int getSize(void* handle);
	Export bool isEmpty(void* handle);

	Export void push(void* handle, int value);

	Export int pop(void* handle);
	
	Export int display(void* handle, int* buffer, int buffer_size);
}