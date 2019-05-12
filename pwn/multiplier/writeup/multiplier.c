#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

typedef unsigned char u8;
typedef unsigned short u16;

typedef struct {
    u8 *buf;
    int len;
} BigNum;

static inline
u8 mulhi8(u8 a, u8 b) {
    u16 prod = a * (u16)b;
    return prod >> 8;
}
static inline
u8 addhi8(u8 a, u8 b) {
    u16 prod = a + (u16)b;
    return prod >> 8;
}

void multiply(BigNum *num, u8 x) {
    if (x == 0) {
        num->buf[0] = 0;
        num->len = 1;
        return;
    }
    int len = num->len;
    u8 carry = 0;
    int i = 0;
    for (; i < len; i++) {
        u8 y = num->buf[i];
        u8 z = x * y;
        num->buf[i] = carry + z;
        carry = mulhi8(x, y) + addhi8(carry, z);
    }
    if (carry != 0) {
        num->buf[len] = carry;
        num->len++;
    }
}

void print(BigNum *num) {
    int fst = 1;
    for (long long i = (num->len / 8 + (num->len % 8 != 0)) - 1; i >= 0; i--) {
        if (fst) {
            printf("%llx", ((unsigned long long *)num->buf)[i]);
            fst = 0;
        } else {
            printf("%016llx", ((unsigned long long *)num->buf)[i]);
        }
    }
    printf("\n");
}

void bye()
{
    exit(-1);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    alarm(30);

    u8 input;
    BigNum num;

    puts("I will multiply odd numbers until you enter 0");
    for(;;){
        puts("");
        u8 buf[16] = {0};
        buf[0] = 1;
        num.buf = buf;
        num.len = 1;

        for (;;) {
            unsigned x;
            if (scanf("%u", &x) != 1)
                bye();
            if (x > 255) {
                puts("1byte positive integer is only available");
                bye();
            }
            input = x & 0xff;
            if (input == 0) {
                break;
            }
            if (input % 2 == 0) {
                puts("I'm able to multiply only odd numbers.");
                return -1;
            }
            multiply(&num, input);
        }
        print(&num);
    }
}
