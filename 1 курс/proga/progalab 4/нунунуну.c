#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

int main() {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    // � UTF-8 ���� ���᪨� ᨬ����
    int *stack = 0;
    int size = 0;
    int capacity = 0;
    int choice = 0;
    do {
        printf("���� �����樨: \n");
        printf("1. ������� �⥪ \n");
        printf("2. ������� �⥪ \n");
        printf("3. �������� ������� \n");
        printf("4. ������� ������� \n");
        printf("5. �������� �� �������� �⥪�\n");
        printf("6. ������᪨� ᤢ��\n");
        printf("0. ��室 �� 横��\n");
        printf("�롮�:");
        scanf("%d", &choice);
        switch (choice) {
            case 1: {
                printf("1. ������ ࠧ��� �⥪�: ");
                scanf("%d", &capacity);
                if (capacity <= 0) {
                    printf("�����४�� ࠧ��� \n");
                    stack = NULL;
                    size = 0;
                    capacity = 0;
                    break;
                }
                stack = (int *)malloc(capacity * sizeof(int));
                break;
            }
            case 2: {
                free(stack);
                stack = NULL;
                size = 0;
                capacity = 0;
                printf("�⥪ ����⨫�\n");
                break;
            }
            case 3: {
                if (stack == NULL) {
                    printf("�⥪ �� ᮧ���\n");
                    break;
                }
                if (size == capacity) {
                    printf("�⥪ ��९�����\n");
                    break;
                }
                printf("������ ���祭��:");
                scanf("%d", &stack[size]);
                size++;
                printf("������� ��������\n");
                break;
            }
            case 4: {
                if (size == 0) {
                    printf("�⥪ ����\n");
                    break;
                }
                printf("������� 㤠���\n", stack[size-1]);
                size--;
                break;
            }
            case 5: {
                if (size == 0) {
                    printf("�⥪ ����\n");
                    break;
                }
                printf("�⥪ (%d ������⮢):\n",size);
                for (int i = size - 1; i >= 0; i--) {
                    printf("%d\n", stack[i]);
                }
                break;
            }
            case 6: {
                if (size == 0) {
                    printf("�⥪ ����\n");
                    break;
                }
                int k, dir;
                printf("������ ������⢮ ᤢ����: ");
                scanf("%d", &k);
                printf("���ࠢ����� (1 - �����, 2 - ����):");
                scanf("%d", &dir);
                k%= size;
                int *temp = malloc(size * sizeof(int));
                for (int i = 0; i < size; i++) {
                    int new_index;
                    if (dir == 1) {
                        new_index = i+k; // ��ࠢ� �⭮�⥫쭮 ���ᨢ� � ����� �᫨ �⥪
                    } else if (dir == 2) {
                        new_index = i-k;
                    }
                    if (new_index >= size) new_index -= size;
                    if (new_index < 0) new_index += size;
                    temp[i] = stack[new_index];
                }
                for (int i = 0; i < size; i++) {
                    stack[i]=temp[i];
                }
                printf("����� �믮����\n");
               break;
            }
                case 0: {
                printf("��室\n");
                break;
            }
                default:printf("������ �㭪� ����\n");

        }

    } while (choice != 0);
    free(stack);
    return 0;
}