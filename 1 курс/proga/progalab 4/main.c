#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <windows.h>

typedef int t;
typedef struct node_tag {
    t value; 
    struct node_tag *next;
} node;

    void arrow(int realpos, int arrowpos) { 
        if (realpos == arrowpos) printf(" >>> ");
        else printf("     ");
    }
void push(node **head, t value) {
    node *tmp = malloc(sizeof(node));
    tmp->next = *head;
    tmp->value = value;
    *head = tmp;
}
t pop(node **head) {
    node *out;
    t value;
    out = *head;
    *head = (*head)->next;
    value = out->value;
    free(out);
    return value;
}
void display(node *head) {
    printf("Стек:\n");
    while (head) {
            printf("%d\n", head->value);
            head = head->next;
    }
}
t getsize(node *head) {
    t size = 0;
    while (head) {
            size++;
            head = head->next;
    }
    return size;
}

void clear(node **head) {
    node *out;
    t value;
    out = *head;
    *head = (*head)->next;
    value = out->value;
    free(out);
}
int main() {
    system("cls");
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    node *head = NULL;
    t summ, push_num, popd;
    int pos = 1;
    int key = 0;
    int size;
    #define MAX 6
    #define MIN 1
    char *mes[MAX] = {
        "1. Вставка", 
        "2. Забрать сверху",
        "3. Отобразить",
        "4. Очистка", 
        "5. Размер", 
    };
    while (key != 27) {
        system("cls");
        for (int i = 0; i < MAX; i++) {
            arrow(i+1, pos);
            printf("%s\n", mes[i]);
        }
        key = getch();
        if (key == 80 && pos != MAX) pos++;
        else if (key == 72 && pos != MIN) pos--;
        if (key == 13) {
            switch (pos) {
                case 1: { 
                    system("cls");
                    printf("Введите число\n");
                    scanf("%d", &push_num);
                    push(&head, push_num);
                    system("pause");
                    break;
                }
                case 2: {
                    system("cls");
                    if (getsize(head) == 0) printf("Стек пуст\n");
                    else {
                        popd = pop(&head);
                        printf("Изъятый элемент: %d\n", popd);
                    }
                    system("pause");
                    break;
                }
                case 3: {
                    system("cls");
                    display(head);
                    system("pause");    
                    break;
                }
                case 4: {
                    system("cls");
                    while (getsize(head) > 0) clear(&head);
                    printf("Стек очищен\n");
                    system("pause");
                    break;
                }
                case 5: {
                    system("cls");
                    size = getsize(head);
                    printf("Размер = %d\n", size);
                    system("pause");
                    break;
                }
                            }
                        }
                    }
                    return 0;
                }

            