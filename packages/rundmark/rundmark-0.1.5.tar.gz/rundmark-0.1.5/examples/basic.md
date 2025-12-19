# 基本的なテスト

```bash{run="Working directory of the task"}
pwd
```

長い出力のテスト
```bash
seq 100
```

```bash{run="fail test"}
echo failing
sleep 1
false
```

```json{file=/tmp/test.json}
{
  "name": "John",
  "age": 30
}
```

```bash{run="View the JSON file"}
cat /tmp/test.json
```

```bash{run="Delete the JSON file"}
rm /tmp/test.json
```
