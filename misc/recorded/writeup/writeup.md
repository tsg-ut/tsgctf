# Recorded Writeup

## 解法
まず、input から キーボード入力を復元すると、だいたい
```
cat /dev/input/event1 > input &
rm /dev/urandom
rm /dev/random
LANG=C date --utc > /dev/random
echo nyan >> /dev/random
curl -O https://www.openssl.org/source/openssl-1.1.1b.tar.gz
tar xzvf openssl-1.1.1b.tar.gz
cd openssl-1.1.1b/
vim crypto/random/rand_unix.c
637Gd17d621Gd2d603Gdd480Gd30d:wq
vim crypto/random/rand_lib.c
250Gd2d:wq
./config
make -j 4
cd ..
LD_LIBRARY_PATH=./openssl-1.1.1b ./openssl-1.1.1b/apps/openssl genrsa 1024 > key.pem
LD_LIBRARY_PATH=./openssl-1.1.1b ./openssl-1.1.1b/apps/openssl rsautl -encrypt -inkey key.pem -in flag.txt -out encrypted
fg 1
```
のようなコマンドが実行されたことがわかる。([daihon.txt](daihon.txt))
`LD_LIBRARY_PATH=./openssl-1.1.1b ./openssl-1.1.1b/apps/openssl genrsa 1024 > key.pem` で鍵を作ってそれを用いてflagを暗号化しているので、 key.pem をどうにかして再生成すればよい。
ところで、鍵の生成に使ったopensslは、 `curl -O https://www.openssl.org/source/openssl-1.1.1b.tar.gz` で落としてきたopensslのソースに対して、 `crypto/random/rand_lib.c` と ` crypto/random/rand_unix.c ` に手を加えてコンパイルをしてできたものである。
`crypto/random/rand_unix.c` の変更箇所近くを見ると、time()の値と pid を予測すればよいことがわかる。
time()の値はinput中のキーボード入力タイミングから分かる。あとはpidを下から全探索して正しくdecryptできるpidを見つければ良い。



## Flag

`TSGCTF{openssl_genrsa_is_hardly_predictable}`
