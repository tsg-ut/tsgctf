#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#include"code.h"

#define rep(i,n) for(int i=0;i<((int)(n));i++)

#define CODESIZE 10000
long long int mem[CODESIZE];

int jmps[CODESIZE];


/*
two pointers.

*/

int init_rec(int i){
	int ti;
	for(;;){
		switch(code[i]){
		case '[':
			ti = init_rec(i+1);
			jmps[i] = ti;
			jmps[ti] = i;
			//printf("%d %d\n",i,ti);
			i = ti+1;
			break;
		case ']':
			return i;
		case '\0':
			return -1;
		default:
			i++;
			break;
		}
	}
}

void init(){
	memset(jmps,-1,sizeof(jmps));
	init_rec(0);
}

#define MOD 65537

int main(){
	//scanf("%s",code);
	init();
	int ip=0,mp=0;
	long long int reg = 0;
	int i,j;
	int iscode;
	while(0 <= ip){
		//printf("%d ",ip);
		switch(code[ip]){
		case '+':
			mem[mp] = (mem[mp]+1)%MOD;
			break;
		case '-':
			mem[mp] = (mem[mp]+MOD-1)%MOD;
			break;
		case '>':
			mp++;
			break;
		case '<':
			mp--;
			break;
		case '[':
			if(mem[mp]==0){
				ip = jmps[ip];
				if(ip<0){
					puts("Unbalanced [");
					exit(-1);
				}
			}
			break;
		case ']':
			if(mem[mp]!=0){
				ip = jmps[ip];
				if(ip<0){
					puts("Unbalanced ]");
					exit(-1);
				}
			}
			break;
		case '=':
			if(mem[mp]==mem[mp+1]){
				mem[mp]=1;
			}
			else{
				mem[mp]=0;
			}
			break;
		case ',':
			mem[mp] = getchar();
			break;
		case '.':
			printf("%c",((unsigned char)(mem[mp] & 255)));
			fflush(stdout);
			break;
		case '\0':
			return 0;
		case 'l':
			reg = mem[mp];
			break;
		case 's':
			mem[mp] = reg;
			break;
		case 'z':
			mem[mp] = 0;
			break;
		case 'a':
			mem[mp] = (mem[mp]+mem[mp+1])%MOD;
			break;
		case 'm':
			mem[mp] = (mem[mp]*mem[mp+1])%MOD;
			break;
		case '#':
			/*
			//break;
			printf("reg :: %lld\n",reg);
			iscode = 1;
			for(i=0;i<200;i++){
				printf(" %c%2d",i==mp?'*':' ',mem[i]);
				if(iscode){
					if(i%7==6){
						puts("");
						if(mem[i+1]!=0){
							iscode=0;
							j = 4;
						}
					}
				}
				else{
					if(j>0)j--;
					else{
						j = 3;
						puts("");
					}
				}
			}
			puts("");
			*/
			break;
		default:
			printf("unknown character %c",code[ip]);
			return -1;
		}
		ip++;
	}
}
