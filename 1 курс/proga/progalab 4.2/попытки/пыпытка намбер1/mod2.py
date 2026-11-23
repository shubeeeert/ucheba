import time
import random

random.seed(time.time())

class Node:
    def __init__(self, value=0):
        self.value = value
        self.next = None


def make():
    ptr = Node(0)
    return ptr


def push(head_ref: list, value: int):
    tmp = Node(value)
    tmp.next = head_ref[0]
    head_ref[0] = tmp


def pop(head_ref: list) -> int:
    if head_ref[0] is None:
        raise IndexError("Список пуст")
    
    out = head_ref[0]
    head_ref[0] = out.next
    value = out.value
    del out
    return value


def clear(head_ref: list):
    if head_ref[0] is None:
        return
    
    out = head_ref[0]
    head_ref[0] = out.next
    del out


def destroy(handle: Node):
    head_ref = [handle]
    while head_ref[0] is not None:
        clear(head_ref)


def get_size(head: Node) -> int:
    size = 0
    current = head
    while current is not None:
        size += 1
        current = current.next
    return size


def is_empty(handle: Node) -> bool:
    return handle.value == 0


def display(handle: Node, buffer_size: int) -> list:
    if handle is None:
        return []
    
    buffer = []
    
    if handle.value <= buffer_size:
        ptr = handle.next
        while ptr is not None:
            if len(buffer) >= buffer_size:
                break
            buffer.append(ptr.value)
            ptr = ptr.next
    
    return buffer
