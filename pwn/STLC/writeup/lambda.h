typedef map<string,Type*> EnvTy;

struct Lambda{
	virtual string str() = 0;
	virtual Lambda* subst(string nv,Lambda* la) = 0;
	virtual Lambda* copy() = 0;
	virtual Lambda* reduce(map<string,Lambda*> env) = 0;
	virtual Type* get_type(EnvTy env) = 0;
	virtual Lambda* apply(Lambda* la,map<string,Lambda*> env){
		cout << "invalid application" << endl;
		exit(-1);
	}
};

typedef map<string,Lambda*> EnvLam;

struct Var : Lambda{
	string var;
	Var(string v){ var = v; }
	string str(){
		return var;
	}
	Lambda* copy(){
		return new Var(var);
	}
	Lambda* subst(string nv,Lambda* la){
		if(nv == var)return la->copy();
		else return this->copy();
	}
	
	Type* get_type(EnvTy env){
		if(env.find(var) == env.end()){
			cout << var << " is free variable" << endl;
			return NULL;
		}
		return env[var];
	}
	Lambda* reduce(EnvLam env){
		if(env.find(var) == env.end())return NULL;
		return env[var]->copy();
	}
};

struct Int : Lambda{
	int var;
	Int(int v){ var = v; }
	string str(){
		return to_string(var);
	}
	Lambda* copy(){
		return new Int(var);
	}
	Lambda* subst(string nv,Lambda* la){
		return this->copy();
	}
	
	Type* get_type(EnvTy env){
		return new TyVar("I");
	}

	Lambda* reduce(EnvLam env){
		return NULL;
	}
};

struct Abs : Lambda{
	Lambda* body;
	string var;
	Type* ty;
	Abs(string v,Type* t,Lambda* bo){ var = v; ty = t; body = bo; }
	string str(){
		return "(\\" + var + ":" + ty->str() + "." + body->str() + ")";
	}
	Lambda* copy(){
		return new Abs(var,ty,body->copy());
	}
	Lambda* subst(string nv,Lambda* la){
		if(nv == var)return this->copy();
		else return new Abs(var,ty,body->subst(nv,la));
	}

	Type* get_type(EnvTy env){
		EnvTy toenv(env);
		toenv[var] = ty;
		Type* bt = body->get_type(toenv);
		if(bt == NULL)return NULL;
		return new TyArrow(ty,bt);
	}
	
	Lambda* apply(Lambda* la,EnvLam env){
		return body->subst(var,la);
	}
	
	Lambda* reduce(EnvLam env){
		return NULL;
	}
};

struct App : Lambda{
	Lambda *expr1,*expr2;
	App(Lambda *e1,Lambda *e2){ expr1 = e1; expr2 = e2; }
	string str(){
		return "(" + expr1->str() + " " + expr2->str() + ")";
	}
	Lambda* copy(){
		return new App(expr1->copy(),expr2->copy());
	}
	Lambda* subst(string nv,Lambda* la){
		return new App(expr1->subst(nv,la),expr2->subst(nv,la));
	}
	
	Type* get_type(EnvTy env){
		Type* t1 = expr1->get_type(env);
		Type* t2 = expr2->get_type(env);
		if(t1==NULL || t2==NULL)return NULL;
		if(t1->tag == TypeTag::TyTagArrow && ((TyArrow*)t1)->ty1->same(t2)){
			return ((TyArrow*)t1)->ty2;
		}
		else{
			cout << "type mismatched for typing " << this->str() << endl;
			cout << "with applying " << t1->str() << " to " << t2->str() << endl;
			return NULL;
		}
	}
	
	Lambda* reduce(EnvLam env){
		Lambda* te1 = expr1->reduce(env);
		if(te1 != NULL){
			return new App(te1,expr2);
		}
		return expr1->apply(expr2,env);
	}
};


struct Decrement : Lambda{
	Decrement(){}
	string str(){
		return "dec";
	}
	Lambda* copy(){
		return new Decrement();
	}
	Lambda* subst(string nv,Lambda* la){
		return this->copy();
	}

	Type* get_type(EnvTy env){
		return new TyArrow(new TyVar("I"),new TyVar("I"));
	}

	Lambda* apply(Lambda* la,EnvLam env){
		Lambda* tla = la->reduce(env);
		if(tla != NULL){
			return new App(this,tla);
		}
		// if la is value, decrement it.
		((Int*)la)->var-=1;
		return la;
	}
	
	Lambda* reduce(EnvLam env){
		return NULL;
	}
};



