#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>
#include <windows.h>
#include <string.h>

typedef struct { // тип структуры стека
    int *collection;
    int capacity;
    int size;
} Stack;

int input() {
    int num;
    printf("Введите число\n");
    scanf("%d\n", &num);
    return num;
}

Stack *create_stack(int capacity) { // создание стека
    if (capacity <= 0) return NULL;
    Stack *stack = malloc(sizeof(Stack));
    if (stack == NULL) return NULL;
    stack->collection = malloc(sizeof(int) * capacity);
    if (stack->collection == NULL) {
        free(stack);
        return NULL;
    }
    stack->capacity = capacity;
    stack->size = 0;
    return stack;
}

void destroy_stack(Stack *stack) { // уничтожение стека
    free(stack->collection);
    free(stack);
}

bool is_full(Stack *stack){ // проверка на полноту
    return stack->capacity == stack->size;
}

bool is_empty(Stack *stack) { // проверка на пустоту
    return stack->size == 0;
}

bool pop(Stack *stack, int *item) { // извлечение элемента с вершины стека
    if (is_empty(stack)) return false;
    stack->size--;
    *item = stack->collection[stack->size];
    return true;
}

bool push(Stack *stack, int item) { // добавление элемента на вершину стека
    if (is_full(stack)) return false;
    stack->collection[stack->size] = item;
    stack->size++;
    return true;
}

bool peek(Stack *stack, int *item) { // просмотр элемента
    if (is_empty(stack)) return false;
    *item = stack->collection[stack->size - 1]; 
    return true;
}

void arrow(int realpos, int arrowpos) { // стрелочка
    if (realpos == arrowpos) printf(" >>> ");
    else printf("     ");
}

void menu() {
    system("cls");
    Stack *stack;
    int pos = 1, created = 0, push_num;
    int keypressed = 0;

    #define MAX 9
    #define MIN 1

    while (keypressed != 27) {
        system("cls");

        arrow(1,pos); printf("1. Создать стек\n");
        arrow(2,pos); printf("2. Удалить стек\n");
        arrow(3,pos); printf("3. Push\n");
        arrow(4,pos); printf("4. Pop\n");
        arrow(5,pos); printf("5. Показ стека\n");
        arrow(6,pos); printf("6. Размер\n");
        arrow(7,pos); printf("7. Пустой?\n");
        arrow(8,pos); printf("8. Peek\n");
        arrow(9,pos); printf("9. агага\n");

        keypressed = getch();
        if (keypressed == 80 && pos != MAX) pos++;
        else if (keypressed == 72 && pos != MIN) pos--;
        else pos = pos;

        if (keypressed == 13) {
            switch (pos) {
                case 1: {
                    system("cls");
                    if (created == 1) {
                        printf("Стек уже создан\n");
                        system("pause");
                        break;
                    }
                    int c_size;
                    printf("Размер?\n");
                    scanf("%d", &c_size);
                    stack = create_stack(c_size);
                    if (stack == NULL) printf("Ошибка\n");
                    else {
                        printf("Стек создан\n");
                        created = 1;
                    }
                    system("pause");
                    break;
                }
                case 2: {
                    system("cls");
                    if (created == 1) {
                        destroy_stack(stack);
                        created = 0;
                        printf("Стек удален\n");

                    }
                    else printf("Стек еще не создан\n");
                    system("pause");
                    break;
                }
                case 3: {
                    system("cls");
                    if (created == 0) printf("Стек еще не создан\n");
                    else if (is_full(stack) == true) printf("Стек заполнен\n");
                    else {
                        push_num = input();
                        push(stack, push_num);
                    }
                    system("pause");
                    break;
                }
                case 4: {
                    system("cls");
                    if (created == 0) printf("Стек еще не создан\n");
                    else if (is_empty(stack) == true) printf("Стек пуст\n");
                    else {
                        int pop_val = 0;
                        pop(stack, &pop_val);
                        printf("Изъятый элемент: %d\n", pop_val);
                    }
                    system("pause");
                    break;
                }
                case 5: {
                    system("cls");
                    if (created == 0) printf("Стек еще не создан\n");
                    else if (is_empty(stack) == true) printf("Стек пуст\n");
                    else {
                        for (int i = 1; i <= stack->size; i++) {
                            int element;
                            element = stack->collection[stack->size - i];
                            printf("%d\n", element);
                        }
                    }
                    system("pause");
                    break;
                }
            }
        }
    }
    
}


int main() {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    menu();
    return 0;
}