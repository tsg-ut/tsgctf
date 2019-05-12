#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>

const int TYPE_DIR = 1;
const int TYPE_FILE = 2;

const int REGULAR_FILE_TYPE = 0;
const int LONG_FILE_TYPE = 1;

#define NAME_SIZE 38
#define N_FILES 89
#define DATA_SIZE 80

#define BLOCK_SIZE 128
#define N_BLOCKS 256

#define FS_SIZE (BLOCK_SIZE * N_BLOCKS)

typedef unsigned char uint8_t;

typedef struct
{
    char type;
    char name[NAME_SIZE];
    uint8_t files[N_FILES];
} __attribute__((__packed__)) Dir;

typedef struct __attribute__((__packed__))
{
    char type;
    char name[NAME_SIZE];
    char file_type;
    void *ptr;
    char data[DATA_SIZE];
} File;

void loop(Dir *cur);

void bye()
{
    exit(-1);
}

void *fs;
Dir *init_fs()
{
    assert(sizeof(File) == sizeof(Dir));
    assert(sizeof(File) == BLOCK_SIZE);

    char *data = malloc(FS_SIZE + 0x10);
    if (data == NULL)
    {
        bye();
    }
    memset(data, 0, FS_SIZE);

    // initialize root dir
    Dir *d = (Dir *)data;
    d->type = TYPE_DIR;
    strncpy(d->name, "root", 4);
    fs = data;
    return d;
}

int create_dir(char *name)
{
    Dir *dirs = (Dir *)fs;
    for (int i = 0; i < N_BLOCKS; i++)
    {
        if (dirs[i].type == 0)
        {
            dirs[i].type = TYPE_DIR;
            strncpy(dirs[i].name, name, NAME_SIZE);
            return i;
        }
    }
    bye();
}

int create_file(char *name)
{
    File *files = (File *)fs;
    for (int i = 0; i < N_BLOCKS; i++)
    {
        if (files[i].type == 0)
        {
            files[i].type = TYPE_FILE;
            strncpy(files[i].name, name, NAME_SIZE);
            return i;
        }
    }
    bye();
}

void hello()
{
    printf("Command Guide\n");
    printf("1: list dir\n");
    printf("2: add file\n");
    printf("3: add dir\n");
    printf("4: show file\n");
    printf("5: change directory\n");
    printf("6: remove file\n");
    printf("7: quit\n");
}

int get_command(Dir *cur)
{
    printf("\n");
    printf("--------------------\n");
    printf("current dir: %s\n", cur->name);
    printf("--------------------\n");
    printf("> ");
    int c;
    if (scanf("%d", &c) != 1)
        bye();
    return c;
}

File *get_file(uint8_t index)
{
    return &((File *)fs)[index];
}

void list_dir(Dir *cur)
{
    for (int i = 0; i < N_FILES; i++)
    {
        uint8_t index = cur->files[i];
        if (index != 0)
        {
            File *f = get_file(index);
            printf("%s\n", f->name);
        }
    }
}

int get_entry(Dir *cur)
{
    for (int i = 0; i < N_FILES; i++)
    {
        uint8_t index = cur->files[i];
        if (index == 0)
        {
            return i;
        }
    }
    printf("you cannot contain more than %d files in a directory\n", N_FILES);
    bye();
}

void add_file(Dir *cur)
{
    int entry = get_entry(cur);

    unsigned size;
    char name[38];
    printf("name: ");
    if (scanf("%37s", name) != 1)
        bye();

    int idx = create_file(name);
    File *f = get_file(idx);

    cur->files[entry] = idx;

    printf("size: ");
    if (scanf("%u", &size) != 1)
        bye();
    if (size > DATA_SIZE)
    {
        f->file_type = LONG_FILE_TYPE;
        if (size + 1 == 0)
            bye();
        f->ptr = malloc(size + 1);
        if (f->ptr == NULL)
        {
            bye();
        }
        memset(f->ptr, 0, size + 1);
        read(0, f->ptr, size);
    }
    else
    {
        f->file_type = REGULAR_FILE_TYPE;
        scanf("%82s", f->data);
    }
}

void add_dir(Dir *cur)
{
    int entry = get_entry(cur);

    char name[38];
    printf("name: ");
    if (scanf("%37s", name) != 1)
        bye();

    int idx = create_dir(name);
    cur->files[entry] = idx;
}

int change_directory(Dir *cur)
{
    char name[38];
    printf("..: parent directory\n");
    printf("name: ");
    if (scanf("%37s", name) != 1)
        bye();

    if (strncmp(name, "..", NAME_SIZE) == 0)
    {
        return 1;
    }

    for (int i = 0; i < N_FILES; i++)
    {
        uint8_t index = cur->files[i];
        if (index != 0)
        {
            Dir *d = (Dir *)get_file(index);
            if (d->type != TYPE_DIR)
                continue;
            if (strncmp(name, d->name, NAME_SIZE) == 0)
            {
                loop(d);
                break;
            }
        }
    }
    return 0;
}

void show_file(Dir *cur)
{
    char name[38];
    printf("name: ");
    if (scanf("%37s", name) != 1)
        bye();

    for (uint8_t i = 0; i < N_FILES; i++)
    {
        uint8_t index = cur->files[i];
        if (index != 0)
        {
            File *f = get_file(index);
            if (f->type != TYPE_FILE)
                continue;
            if (strncmp(name, f->name, NAME_SIZE) == 0)
            {
                if (f->file_type == LONG_FILE_TYPE)
                {
                    printf("%s\n", (char *)f->ptr);
                    return;
                }
                else
                {
                    printf("%s\n", f->data);
                    return;
                }
            }
        }
    }
}

void remove_file(Dir *cur)
{
    char name[38];
    printf("Note: when you remove a directory, files in the directory are not removed.\n");
    printf("name: ");
    if (scanf("%37s", name) != 1)
        bye();

    for (int i = 0; i < N_FILES; i++)
    {
        uint8_t index = cur->files[i];
        if (index != 0)
        {
            File *f = get_file(index);
            if (strncmp(name, f->name, NAME_SIZE) == 0)
            {
                if (f->type == TYPE_FILE && f->file_type == LONG_FILE_TYPE)
                {
                    free(f->ptr);
                }
                memset(f, 0, BLOCK_SIZE);
                cur->files[i] = 0;
            }
        }
    }
}

void loop(Dir *cur)
{
    while (1)
    {
        int c = get_command(cur);
        switch (c)
        {
        case 1:
            list_dir(cur);
            break;
        case 2:
            add_file(cur);
            break;
        case 3:
            add_dir(cur);
            break;
        case 4:
            show_file(cur);
            break;
        case 5:
            if (change_directory(cur))
            {
                return;
            }
            break;
        case 6:
            remove_file(cur);
            break;
        default:
            printf("bye\n");
            bye();
            break;
        }
    }
}

int main(void)
{
    alarm(360);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    hello();
    Dir *root = init_fs();
    loop(root);
    bye();
    return 0;
}
