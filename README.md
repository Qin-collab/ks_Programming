# KS编程语言

KS是一个简洁而强大的编程语言，支持基本的编程构造和现代语言特性。

## 语法特性

### 变量声明
```ks
let x = 10;
let name = "Hello World";
let flag = true;
```

### 函数定义
```ks
func add(a, b) {
    return a + b;
}

func greet(name) {
    print("Hello, " + name + "!");
}
```

### 控制流
```ks
if (x > 5) {
    print("x is greater than 5");
} else {
    print("x is less than or equal to 5");
}

for (let i = 0; i < 10; i = i + 1) {
    print(i);
}

while (flag) {
    print("Running...");
    flag = false;
}
```

### 数据类型
- 整数: `42`
- 浮点数: `3.14`
- 字符串: `"Hello World"`
- 布尔值: `true`, `false`

### 运算符
- 算术: `+`, `-`, `*`, `/`, `%`
- 比较: `==`, `!=`, `<`, `>`, `<=`, `>=`
- 逻辑: `&&`, `||`, `!`

## 使用方法

1. 编写.ks文件
2. 使用编译器编译: `python ks_compiler.py your_file.ks`
3. 运行生成的代码

## 示例程序

```ks
func fibonacci(n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

func main() {
    print("Fibonacci sequence:");
    for (let i = 0; i < 10; i = i + 1) {
        print(fibonacci(i));
    }
}

main();
```
