**The English introduction is placed below the Chinese version.**

一个支持并行反编译的Python反编译工具，多进程并行反编译pyc文件中的每个类和函数。  
同时支持使用`uncompyle6`和`decompyle3`库。  
由于`uncompyle6`和`decompyle3`库是不支持并行的，反编译超过20KB的pyc文件会很慢，  
而且一旦单个函数反编译失败，整个反编译就会停止。  
而这个程序采用了并行，旨在于提高反编译的速度和性能。  
## 1.命令行
```shell
python decompiler.py <要编译的.pyc文件名> <--uncompyle6或--decompyle3开关(可选)>
```
如果不指定开关，则默认使用`uncompyle6`库。  
运行结束后，会自动在pyc文件所在的目录生成一个同名的.py文件，作为反编译结果，如`python decompiler.py test.pyc`会生成`test.py`这个文件。  

## 2.程序的实现原理
pyc文件本身是一个`Code`(字节码)对象，而这个对象的co_const属性的元组内部又包含了函数和类的`Code`对象。  
程序首先预处理pyc文件，将各个函数和类的字节码分离出来，并将函数和类以简单的`return`语句替代。  
然后将预处理之后的pyc文件反编译成.py源文件，此时的源文件只有大致框架，就像下面这样：  
```python
import sys,os

class Test:
    return 123 # 以简单的return语句暂时替代 (虽然并不符合语法)

def test():
    return 125

if __name__=="__main__":test()
```
接着再使用多进程，并行反编译各个函数和类的字节码文件，最后将结果合并，生成最终的代码。  
此外，如果一个函数、类反编译失败，不会影响其他函数、类的反编译。  

## 3.依赖的库
这个反编译工具依赖于`pyobject`库，尤其是`pyobject.code_`这个子模块中的`Code`类。  
`pyobject`库可用`pip install pyobject`命令安装。  

## 4.兼容性
程序支持所有的Python 3版本，由于不依赖于特定版本的字节码。  

## 5.TODO
由于单个类的方法可能会很多，自己未来会考虑使用递归，将类中的各个方法拆分再并行反编译，以进一步提升速度。  


A Python decompiler tool supporting parallel decompilation, designed to decompile each class and function within pyc files using multiple processes. It supports using both `uncompyle6` and `decompyle3` libraries. The `uncompyle6` and `decompyle3` libraries themselves do not support parallel processing, which can result in slow decompilation for pyc files larger than 20KB and can halt the entire decompilation process if a single function fails to decompile. This program utilizes parallel decompilation to enhance the speed and performance of the decompilation process.

## 1. Command Line Usage
```shell
python decompiler.py <filename.pyc> [--uncompyle6 | --decompyle3]
```
If no switch is specified, the `uncompyle6` library is used by default. Upon completion, a .py file with the same name as the pyc file will be generated in the pyc file's directory as the decompilation result. For example, running `python decompiler.py test.pyc` will produce `test.py`.

## 2. Implementation Principle
A pyc file is essentially a `Code` (bytecode) object, and the tuple within its `co_consts` attribute contains the `Code` objects for functions and classes. The program first preprocesses the pyc file, separating the bytecode for each function and class, and replaces them with simple `return` statements. The preprocessed pyc file is then decompiled into a .py source file, which initially contains only a rough framework, as shown below:

```python
import sys
import os

class Test:
    return 123  # Temporarily replaced with a simple return statement (although it is not syntactically valid)

def test():
    return 125

if __name__ == "__main__":
    test()
```

Next, multiple processes are used to parallelly decompile the bytecode files of each function and class. The results are then merged to generate the final code. Additionally, if decompilation of a single function or class fails, it will not affect the decompilation of other functions or classes.

## 3. Dependencies
This decompiler tool depends on the `pyobject` library, particularly the `Code` class from the `pyobject.code_` submodule. The `pyobject` library can be installed with the command `pip install pyobject`.

## 4.Compatibility
The program supports all versions of Python 3 since it doesn't rely on a specific version of bytecode.

## 5. TODO
Since a class may have many methods, future considerations include using recursion to split and parallelly decompile individual methods within a class to further improve speed.
