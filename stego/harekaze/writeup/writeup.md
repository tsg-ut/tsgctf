# Harekaze Writeup

## How to solve

Simply mapping internal expression of (Y, Cb, Cr) values into (R, G, B) produces the following image:

![](harekaze_solve.jpg)

The flag is `TSGCTF{UnderTheBlueSeaMermaidSwims}`

## Theories behind this chal

JPEG uses (Y, Cb, Cr) color space to compress images. This method is basically efficient for compression used with chroma sampling, but technically inefficient from the point of color space view.

Conversion between (Y, Cb, Cr) and (R, G, B) is a linear transformation. It rotates dimension and in principal, (Y, Cb, Cr) color space is _larger_ than (R, G, B) color space. So, there are (Y, Cb, Cr) colors that cannot be converted correctly into (R, G, B) colors.

In this chal, I used following colors for the image background and foreground.

* Background: `(Y, Cb, Cr) = (122, 225, 112)` = `(R, G, B) = (99, 100, 293)`
* Foreground: `(Y, Cb, Cr) = (129, 255, 107)` = `(R, G, B) = (99, 100, 354)`

Both colors have very different tints, but their Blue value excesses 255 and rounded into 255. So, apparently two colors cannot be distinguished when rendered into RGB, keeping internal representation not the same.

---

## 解法

JPEGの色空間がYCbCrであることを利用した問題。

フラグの括弧で囲われた部分を解析すると、絶妙に何かがあることがわかる。

![](harekaze_analyze.png)

が、いくらそのまま画像を操作しても文字列を復元することはできない。

この問題のポイントは、JPEGのエンコードに使用されているYCbCr空間の大きさは、デコードされた状態のRGB空間よりも大きいということを知っているかどうかである。

つまり、JPEGにおいては、YCbCr空間で表せてRGB空間では表せない色というのが存在する。

例えば、`(Y, Cb, Cr) = (129, 255, 107)`という色は`(R, G, B) = (99, 100, 354)`に対応しているが、この色はBの値が上限の255を超えているため、通常は表せない。このような色は通常255を超えた値を255に詰めてRGBに変換されるので、JPEGが表示される際には`(R, G, B) = (99, 100, 255)`に変換される。

今回の問題では、

* 背景: `(Y, Cb, Cr) = (122, 225, 112)` = `(R, G, B) = (99, 100, 293)`
* 前影: `(Y, Cb, Cr) = (129, 255, 107)` = `(R, G, B) = (99, 100, 354)`

でフラグが記載されている。つまりBの値を詰めて255にすると背景と前影が同じ色になって表示されてしまうが、実際の内部表現は全く違う色になっているという寸法である。

これを解く方法はいくつか考えられるが、例えばJPEGの内部のYCbCrをそのままRGBにマッピングして出力すると以下のような画像が得られる。

![](harekaze_solve.jpg)

## Flag

`TSGCTF{UnderTheBlueSeaMermaidSwims}`