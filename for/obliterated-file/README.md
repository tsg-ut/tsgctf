# obliterated-file

## Author

@taiyoslime

## Description

Working on making a problem of TSG CTF, I noticed that I have staged and committed the flag file by mistake before I knew it.
I googled and found the following commands, so I'm not sure but anyway typed them. It should be ok, right?

TSG CTFに向けて問題を作っていたんですが，いつの間にか誤ってflagのファイルをコミットしていたことに気付いた！とにかく，Google先生にお伺いして次のようなコマンドを打ちこみました．よくわからないけどこれできっと大丈夫...？

```
$ git filter-branch --index-filter "git rm -f --ignore-unmatch *flag" --prune-empty -- --all
$ git reflog expire --expire=now --all
$ git gc --aggressive --prune=now
``` 

## Difficulty Estimate

easy-med
