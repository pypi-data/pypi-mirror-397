# Table を実行する

タイトル行をオプションにする

::: run bash a.sh
| -x | -y | opt |
| :--- | :--- | :--- |
| 1    | true | abc |
| 2    | false | def |
| 3    | true |     |

この場合、以下のものを実行し、Result 列を追加して結果を表示する。

```bash{run=no}
bash a.sh -x 1 -y abc
bash a.sh -x 2 def
bash a.sh -x 3 -y
```

a.sh
```bash{file}
if [ "$3" != "-y" ]; then
  echo "error"
  echo "error in stderr" 1>&2
  exit 1
fi
echo $* | tee -a log%                                                         
```

delete
```bash
rm hoge
```
