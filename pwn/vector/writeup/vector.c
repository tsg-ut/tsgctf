#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <stdint.h>

#define DEFAULT_SIZE 1
#define VECTOR_COUNT 100

void bye()
{
    exit(-1);
}

typedef struct
{
    uint16_t size;
    uint16_t cap;
    char data[0];
} Vector;

void clear(Vector *v)
{
    if (v == NULL)
    {
        return;
    }
    free(v);
}

Vector *new (uint16_t cap)
{
    uint16_t size = cap + sizeof(Vector);
    Vector *v = malloc(size);
    if (v == NULL)
    {
        puts("malloc fail");
        bye();
    }

    v->size = 0;
    v->cap = cap;
    return v;
}

void push(Vector **v_store, char val)
{
    Vector *v = *v_store;
    if (v->size == v->cap)
    {
        Vector *w = new (v->cap + 1);
        memcpy(w->data, v->data, v->size);
        w->size = v->size;
        clear(v);
        *v_store = w;
        v = w;
    }
    v->data[v->size] = val;
    v->size++;
}

Vector *concat(Vector *v1, Vector *v2)
{
    uint16_t cap = v1->cap + v2->cap;
    Vector *v = new (cap);
    for (int i = 0; i < v1->size; i++)
    {
        push(&v, v1->data[i]);
    }
    for (int i = 0; i < v2->size; i++)
    {
        push(&v, v2->data[i]);
    }
    return v;
}

void check_index(Vector *v, uint16_t index)
{
    if (index >= v->size)
    {
        puts("Index out of range.");
        bye();
    }
}

char get(Vector *v, uint16_t index)
{
    check_index(v, index);
    return v->data[index];
}

void set(Vector *v, uint16_t index, char val)
{
    check_index(v, index);
    v->data[index] = val;
}

Vector *vectors[VECTOR_COUNT];

Vector *at(int name)
{
    if (name < 0 || name >= VECTOR_COUNT)
    {
        puts("Not found");
        bye();
    }
    Vector *v = vectors[name];
    if (v == NULL)
    {
        puts("Not found");
        bye();
    }
    return v;
}

void set_at(int name, Vector *v)
{
    if (name < 0 || name >= VECTOR_COUNT)
    {
        puts("Not found");
        bye();
    }
    clear(vectors[name]);
    vectors[name] = v;
}

int get_name()
{
    int name;
    printf("(only numbers 0-%d)name: ", VECTOR_COUNT - 1);
    if (scanf("%d", &name) != 1)
        bye();
    return name;
}

char get_val()
{
    int val;
    printf("(only numbers 0-255)value: ");
    if (scanf("%d", &val) != 1)
        bye();
    return (char)val;
}

uint16_t get_index()
{
    int val;
    printf("index: ");
    if (scanf("%u", &val) != 1)
        bye();
    return (uint16_t)val;
}

void command_new()
{
    int name = get_name();
    set_at(name, new (DEFAULT_SIZE));
}

void command_concat()
{
    puts("Please choose two vectors which you want to concatenate");
    int name1 = get_name();
    int name2 = get_name();
    puts("Please enter the destination vector's name");
    int dst_name = get_name();

    Vector *v1 = at(name1);
    Vector *v2 = at(name2);
    set_at(dst_name, concat(v1, v2));
}

void command_push()
{
    int name = get_name();
    char val = get_val();
    Vector *v = at(name);
    push(&v, val);
}

void command_set()
{
    int name = get_name();
    uint16_t index = get_index();
    char val = get_val();
    Vector *v = at(name);
    set(v, index, val);
}

void command_get()
{
    int name = get_name();
    uint16_t index = get_index();
    Vector *v = at(name);
    printf("val: %d\n", get(v, index));
}

void commands()
{
    printf("Commands\n");
    printf("0: quit\n");
    printf("1: new\n");
    printf("2: concat\n");
    printf("3: push\n");
    printf("4: set\n");
    printf("5: get\n");
}

int menu()
{
    printf("\n-------------\n");
    printf("> ");
    int c;
    if (scanf("%d", &c) != 1)
        bye();
    return c;
}
int main()
{
    assert(sizeof(Vector) == 4);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    alarm(60);
    commands();
    while (1)
    {
        int command = menu();
        switch (command)
        {
        case 0:
            puts("bye");
            bye();
            break;
        case 1:
            command_new();
            break;
        case 2:
            command_concat();
            break;
        case 3:
            command_push();
            break;
        case 4:
            command_set();
            break;
        case 5:
            command_get();
            break;
        default:
            //nop
            break;
        }
    }
    bye();
    return 0;
}
