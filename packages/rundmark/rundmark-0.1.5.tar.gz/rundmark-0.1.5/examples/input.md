```bash{run="read from stdin",input}
echo hello
read -p "input any string " user
echo "your input is $user"
```

```behave{run,input}
Feature hello
echo $a
```