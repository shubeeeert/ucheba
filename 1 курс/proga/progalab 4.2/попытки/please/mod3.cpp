#include <stack>
#include <cstdlib>
#include <ctime>

#ifdef _WIN32
#define Export __declspec(dllexport)
#else
#define Export __attribute__((visibility("default")))
#endif

bool initRandom = false;

extern "C" Export void* make() {
    if (!initRandom) {
        srand((unsigned int)time(0));
        initRandom = true;
    }
    return new std::stack<int>();
}

extern "C" Export void push(void* handle, int value) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    stack->push(value);
}

extern "C" Export int pop(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    int value = stack->top();
    stack->pop();
    return value;
}

extern "C" Export void clear(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    while (!stack->empty()) {
        stack->pop();
    }
}

extern "C" Export void destroy(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    delete stack;
}

extern "C" Export int getSize(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    return static_cast<int>(stack->size());
}

extern "C" Export bool isEmpty(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    return stack->empty();
}

extern "C" Export int display(void* handle, int* buffer, int buffer_size) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    if (!buffer || stack->empty()) return 0;

    std::stack<int> tmp = *stack;
    int count = 0;
    while (!tmp.empty() && count < buffer_size) {
        buffer[count] = tmp.top();
        tmp.pop();
        count++;
    }
    return count;
}