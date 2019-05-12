all: problem.cpp parser.h lambda.h type.h
	g++ problem.cpp -o a.out -pie -fPIE -Wl,-z,now,-z,relro -fstack-protector-all
	rm ../problem/stlc-*
	mv a.out ../problem/stlc-`sha1sum a.out | awk '{print $$1}'`
