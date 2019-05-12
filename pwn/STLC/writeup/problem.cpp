#include<cstdio>
#include<iostream>
#include<cstring>
#include<vector>
#include<string>
#include<algorithm>
#include<map>
#include<cctype>
#include<unistd.h>

using namespace std;

#include "type.h"
#include "lambda.h"
#include "parser.h"

int main(){
	alarm(60);

	setvbuf(stdin, NULL, _IONBF, 0); 
	setvbuf(stdout, NULL, _IONBF, 0); 
	
	EnvLam lamenv;
	EnvTy tyenv;
	
	lamenv["dec"] = new Decrement();
	tyenv["dec"] = lamenv["dec"]->get_type(tyenv);
	
	for(string s;cout << "> ",getline(cin,s);){
		string var;
		Lambda* la = parse(s,var);
		if(la == NULL){
			cout << "parse failed" << endl;
			continue;
		}
		if(lamenv.find(var) != lamenv.end()){
			cout << var << " is already defined" << endl;
			continue;
		}
		Type* ty = la->get_type(tyenv);
		if(ty == NULL){
			cout << la->str() << " can't be simply typed" << endl;
			continue;
		}
		for(;;){
			//cout << la->str() << endl;
			Lambda* tla = la->reduce(lamenv);
			if(tla==NULL)break;
			la = tla;
		}
		cout << var << " = " << la->str() << " :: " << ty->str() << endl;
		tyenv[var] = ty;
		lamenv[var] = la;
	}
	return 0;
}
