
enum TypeTag{
	TyTagVar,
	TyTagArrow
};

struct Type{
	TypeTag tag;
	virtual string str() = 0;
	virtual bool same(Type* t) = 0;
};

struct TyVar : Type{
	string var;
	TyVar(string v){ var = v; tag = TypeTag::TyTagVar; }
	string str(){
		return var;
	}
	bool same(Type* t){
		return t->tag == tag && ((TyVar*)t)->var == var;
	}
};

struct TyArrow : Type{
	Type *ty1,*ty2;
	TyArrow(Type* t1,Type* t2){ ty1=t1; ty2=t2; tag = TypeTag::TyTagArrow; }
	string str(){
		return "(" + ty1->str() + "->" + ty2->str() + ")";
	}
	bool same(Type* t){
		return t->tag == tag && ((TyArrow*)t)->ty1->same(ty1) && ((TyArrow*)t)->ty2->same(ty2);
	}
};

