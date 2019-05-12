# eso vm Writeup

## 解法
### 方法1	
VMのコードを解析すると下記のようなコードが実行されていることがわかる。

```
for(i=0;i<34;i++){
	c = getchar();
	for(j=0;j<34;j++){
		c = c * A[j] + B[j];
		s[j] += c;
	}
}

v = 0;
for(j=0;j<34;j++){
	v += (s[j] != Q[j]);
}
if(v==0){
	puts("Correct!\n");
} else {
	puts("Wrong:cry:\n");
}
```
A,B,Qは初期化後のメモリを見ると分かるので、
あとはこれに従って正しい入力文字列を求めればよい。

### 方法2

シンボリック実行するインタプリタ(例として eso_vm_interp_solver.py をあげた)を書く。
入力値に依存して実行パスの変わる部分では、いいかんじの方向に分岐させると"Correct"と出力されるので、
それを満たすようなパスのための制約を解けばよい。

## Flag

`TSGCTF{vm_0n_vm_c4n_be_r3ver5able}`
