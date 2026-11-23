#include "mod.h"
#include <time.h>
#include <stdlib.h>

bool initRandom = false;

struct node {
    int value; 
    struct node *next;
};

Export void* make() {
	if (!initRandom) {
		srand(time(0));
		initRandom = true;
	}
	node* ptr = new node;
	ptr->value = 0;
	ptr->next = nullptr;
	return ptr;
}

Export void push(node **head, int value) {
    node *tmp = new node;
    tmp->next = *head;
    tmp->value = value;
    *head = tmp;
}

Export int pop(node **head) {
    node *out;
    int value;
    out = *head;
    *head = (*head)->next;
    value = out->value;
    delete out;
    return value;
}

Export void clear(node **head) {
    node *out;
    int value;
    out = *head;
    *head = (*head)->next;
    value = out->value;
    delete out;
}

Export void destroy(void* handle) {
	node* tmp = (node*) handle;
	clear(&tmp);
	delete tmp;
}

Export int getSize(node *head) {
    int size = 0;
    while (head) {
            size++;
            head = head->next;
    }
    return size;
}

Export bool isEmpty(void* handle) {
	node* ptr = (node*) handle;
	return ptr->value == 0;
}

Export int display(void* handle, int* buffer, int buffer_size) {
    node* str = (node*) handle;
    if (buffer && str->value <= buffer_size) {
        int count = 0;
        node* ptr = str->next;  
        while (ptr != nullptr) {
            buffer[count] = ptr->value;
            ptr = ptr->next;       
            count++;
        }
        return count;
    }
    return 0;
}
