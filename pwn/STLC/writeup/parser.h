

vector<string> tokenize(string s){
	vector<string> res;
	string rem = "";
	for(auto c : s){
		if(string(" \t\\=:.()->$").find(c) != string::npos){
			if(c == '>' && rem == "" && res.back() == "-"){
				res.pop_back();
				res.push_back("->");
				continue;
			}
			if(rem != "")res.push_back(rem);
			rem = "";
			if(string(" \t").find(c) == string::npos){
				res.push_back(string(1,c));
			}
		}
		else{
			rem += c;
		}
	}
	if(rem != "")res.push_back(rem);
	
	//cout << res.size() << endl;
	//for(auto d : res){	cout << " , " << d; } cout << endl;
	return res;
}

struct token_list{
	vector<string> tokens;
	unsigned int p;
	token_list(vector<string> init){ tokens = init; p=0; }
	string front(){
		if(p >= tokens.size()){
			cerr << "parse error. tokens run out." << endl;
			exit(-1);
		}
		return tokens[p];
	}
	string pop(){
		string res = this->front();
		p += 1;
		return res;
	}
	void expect(string s){
		string ns = this->pop();
		if(ns != s){
			cerr << "parse error. expected \"" << s << "\" but got \"" << ns << "\"." << endl;
			exit(-1);
		}
	}
};

Type* parse_type(token_list* tokens){
	//cout << "parse_type " << tokens->front() << endl;
	
	vector<Type*> ts;
	bool ishead = true;
	for(;tokens->front() != ")" && tokens->front() != ".";){
		if(ishead)ishead = false;
		else tokens->expect("->");
		if(tokens->front() == "("){
			tokens->pop();
			ts.push_back(parse_type(tokens));
			tokens->expect(")");
		}
		else{
			ts.push_back(new TyVar(tokens->pop()));
		}
	}
	Type* res = ts.back();
	ts.pop_back();
	reverse(ts.begin(),ts.end());
	for(auto d : ts){
		res = new TyArrow(d,res);
	}
	return res;
}

Lambda* parse_rec(token_list* tokens){
	//cout << "parse_rec " << tokens->front() << endl;
	if(tokens->front() == "\\"){
		tokens->pop();
		string var = tokens->pop();
		tokens->expect(":");
		Type* t = parse_type(tokens);
		tokens->expect(".");
		Lambda* body = parse_rec(tokens);
		return new Abs(var,t,body);
	}
	else{
		Lambda* res = NULL;
		for(;tokens->front() != ")";){
			Lambda* la;
			if(tokens->front() == "("){
				tokens->pop();
				la = parse_rec(tokens);
				tokens->expect(")");
			}
			else{
				string s = tokens->pop();
				if(all_of(s.cbegin(),s.cend(),[](unsigned char c){return isdigit(c);})){
					la = new Int(stoi(s));
				}
				else{
					la = new Var(s);
				}
			}
			if(res==NULL)res = la;
			else{
				res = new App(res,la);
			}
		}
		return res;
	}
}

Lambda* parse(string ins,string& var){
	vector<string> ts = tokenize(ins);
	if(ts.size() <= 2 || ts[1] != "="){
		return NULL;
	}
	var = ts[0];
	ts.push_back(")");
	token_list tokens(ts);
	tokens.p += 2;
	return parse_rec(&tokens);
}

