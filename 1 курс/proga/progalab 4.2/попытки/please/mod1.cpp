#include <cstdlib>
#include <ctime>

#ifdef _WIN32
#define Export __declspec(dllexport)
#else
#define Export __attribute__((visibility("default")))
#endif

struct Node {
    int data;
    Node* next;
};

struct Stack {
    Node* top;
    int size;
};

bool initRandom = false;

extern "C" Export void* make() {
    if (!initRandom) {
        srand((unsigned int)time(0));
        initRandom = true;
    }
    Stack* stack = new Stack();
    stack->top = nullptr;
    stack->size = 0;
    return static_cast<void*>(stack);
}

extern "C" Export bool isEmpty(void* handle) {
    if (!handle) return true;
    Stack* stack = static_cast<Stack*>(handle);
    return stack->top == nullptr;
}

extern "C" Export void push(void* handle, int value) {
    Stack* stack = static_cast<Stack*>(handle);
    Node* newNode = new Node();
    newNode->data = value;
    newNode->next = stack->top;
    stack->top = newNode;
    stack->size++;
}

extern "C" Export int pop(void* handle) {
    Stack* stack = static_cast<Stack*>(handle);
    if (isEmpty(handle)) return -1;
    Node* temp = stack->top;
    int value = temp->data;
    stack->top = stack->top->next;
    delete temp;
    stack->size--;
    return value;
}

extern "C" Export void clear(void* handle) {
    Stack* stack = static_cast<Stack*>(handle);
    while (stack->top) {
        Node* temp = stack->top;
        stack->top = stack->top->next;
        delete temp;
    }
    stack->size = 0;
}

extern "C" Export void destroy(void* handle) {
    if (!handle) return;
    clear(handle);
    delete static_cast<Stack*>(handle);
}

extern "C" Export int getSize(void* handle) {
    Stack* stack = static_cast<Stack*>(handle);
    return stack->size;
}

extern "C" Export int display(void* handle, int* buffer, int buffer_size) {
    Stack* stack = static_cast<Stack*>(handle);
    if (!buffer || !stack || stack->size == 0) return 0;
    Node* ptr = stack->top;
    int count = 0;
    while (ptr != nullptr && count < buffer_size) {
        buffer[count] = ptr->data;
        ptr = ptr->next;
        count++;
    }
    return count;
}