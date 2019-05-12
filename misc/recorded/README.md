# Recorded

## Author

@satos

## Description

What's happend?

何が起こった？

```
$ sudo docker build -t problem .
$ sudo docker run -it --device=/dev/input/event1:/dev/input/event1 problem "/bin/bash"
root@hogehuga:/tmp# cat /dev/input/event1 > input &
```

**Note** The foregoing commands were typed with the **JIS** keyboard, not US keyboard.

**注意** これらのコマンドはJISキーボードのパソコンで実行されました。


## Difficulty Estimate

medium
