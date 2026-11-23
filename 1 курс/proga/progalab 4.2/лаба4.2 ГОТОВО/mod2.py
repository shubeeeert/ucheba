import random
import time

class Node:
    def __init__(self, value=0):
        self.value = value
        self.next = None

class Stack:
    def __init__(self):
        self.top = None
        self.size = 0

random.seed(time.time())

def make():
    return Stack()

def push(handle, value):
    new_node = Node(value)
    new_node.next = handle.top
    handle.top = new_node
    handle.size += 1

def pop(handle):
    if handle.top is None:
        raise IndexError("Стек пуст")
    node = handle.top
    handle.top = node.next
    handle.size -= 1
    return node.value

def clear(handle):
    handle.top = None
    handle.size = 0

def destroy(handle):
    clear(handle)

def getSize(handle):
    return handle.size

def isEmpty(handle):
    return handle.top is None

def display(handle, buffer, buffer_size):
    if handle.top is None:
        return 0
    count = 0
    ptr = handle.top
    try:
        while ptr is not None and count < buffer_size:
            buffer[count] = ptr.value
            ptr = ptr.next
            count += 1
        return count
    except Exception:
        result = []
        ptr = handle.top
        while ptr is not None:
            result.append(ptr.value)
            ptr = ptr.next
        return result