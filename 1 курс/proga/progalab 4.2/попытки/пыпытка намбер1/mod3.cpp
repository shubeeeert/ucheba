#include "mod.h"
#include <stack>
#include <ctime>
#include <cstdlib>

bool initRandom = false;

Export void* make() {
    if (!initRandom) {
        srand(time(0));
        initRandom = true;
    }
    return new std::stack<int>();
}

Export void push(void* handle, int value) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    stack->push(value);
}

Export int pop(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    int value = stack->top();
    stack->pop();
    return value;
}

Export void clear(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    while (!stack->empty()) {
        stack->pop();
    }
}

Export void destroy(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    delete stack;
}

Export int getSize(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    return static_cast<int>(stack->size());
}

Export bool isEmpty(void* handle) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);
    return stack->empty();
}

Export int display(void* handle, int* buffer, int buffer_size) {
    std::stack<int>* stack = static_cast<std::stack<int>*>(handle);

    if (!buffer || stack->empty()) {
        return 0;
    }

    std::stack<int> tmp = *stack;
    std::stack<int> reversed;

    while (!tmp.empty()) {
        reversed.push(tmp.top());
        tmp.pop();
    }

    int count = 0;
    while (!reversed.empty() && count < buffer_size) {
        buffer[count] = reversed.top();
        reversed.pop();
        count++;
    }

    return count;
}