# Millionaire Girl Writeup

Node.jsの`Math.random()`を予測する問題。ポイントはもちろん、得られた乱数の一部のビットしか情報として得られないということ。

package.jsonを見れば分かる通り、ランタイムのNode.jsのバージョンは11.11.0が使用されている。 https://nodejs.org/en/download/releases/ を見ればわかるが、このバージョンにバンドルされているv8のバージョンは7.0.276.38なので、この実装を読む。

* https://github.com/v8/v8/blob/7.0.276.38/src/runtime/runtime-maths.cc#L59-L64
* https://github.com/v8/v8/blob/7.0.276.38/src/base/utils/random-number-generator.h#L111-L129

読むべき実装はこのあたりだが、要はMath.random()の実装はXorshift128+である。これはV8のブログでも詳しく解説されている。

* [There’s Math.random(), and then there’s Math.random() · V8](https://v8.dev/blog/math-random)

そして一般的な事実として、Xorshiftの出力は、完全な出力が与えられればSATソルバを用いて容易に予測可能である。ももテクにもそう書いてある。

* [Z3Pyでxorshift128+の出力を推測してみる - ももいろテクノロジー](http://inaz2.hatenablog.com/entry/2016/03/07/194034)

なので概ね上の記事と同じくZ3Pyを用いて乱数予測してあげればよいのだが、注意点として、この問題ではXorShift128の出力である64ビット整数のうち一部の情報しか与えられない。

まずV8のToDoubleの実装を見れば分かる通り、V8では64ビットのうち上位12ビットの情報を切り捨てて出力している。

加えて、サーバーから情報として得られるのは一つの乱数につき0から5の数字16個なので、情報量としては `log2(6 ** 16) = 41.36bit` となる。桁またぎを考慮すると確実に正しいと言えるのはせいぜい32bit程度と考えられる。

つまり64bitのうちの上位12bitと下位20bitを除いた真ん中の32bitから乱数を推測することを考える。これはZ3Pyを用いて次のような制約を課すことで表現できる。

```py
solver.add((output & 0xFFFFFFFF00000) == int(generated[i]))
```

もう一つ注意点として、このバージョンのV8では乱数をキャッシュして利用しているため、XorShiftの逆回しの順に乱数が出てくる。これは下のブログ記事に詳しい。

* [XorShift128+ Backward – Independent Security Evaluators](https://blog.securityevaluators.com/xorshift128-backward-ff3365dc0c17)

よってこのブログなどの実装を参考にしてXorShiftの逆回しを実装する必要がある。

以上に気をつければ難なく解答することができるだろう。

ちなみにこのゲームの元ネタは[ペニーガール](https://dic.pixiv.net/a/%E3%83%9A%E3%83%8B%E3%83%BC%E3%82%AC%E3%83%BC%E3%83%AB)である。
