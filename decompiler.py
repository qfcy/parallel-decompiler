from pyobject.code_ import Code
try:
    from importlib._bootstrap_external import MAGIC_NUMBER
except ImportError:
    from importlib._bootstrap import MAGIC_NUMBER
from types import CodeType
import sys,os,subprocess,marshal
from warnings import warn

def _wait_process(processes,max_parallel):
    # 等待多余的进程完成
    global completed,failed
    while len(processes)>max_parallel:
        i=0
        while i<len(processes):
            proc=processes[i]
            if proc.poll() is not None:
                completed+=1
                if proc.returncode==0:
                    print("%s 反编译完成 (%d/%d)"%(os.path.split(proc.args[2])[1],
                            completed,len(original_code)))
                else:
                    print("%s 反编译失败, 状态码: %d (%d/%d)"%(os.path.split(proc.args[2])[1],
                            proc.returncode,completed,len(original_code)))
                    failed+=1
                del processes[i]
            else:
                i+=1

if len(sys.argv)<2 or "-h" in sys.argv:
    print("用法: python %s <一个或多个.pyc文件名> <--uncompyle6或--decompyle3>" % sys.argv[0])
    sys.exit(1)
if "--decompyle3" in sys.argv:
    decomp_script="decompyle_3.py"
    print("当前使用 decompyle3 库")
    sys.argv.remove("--decompyle3")
else:
    decomp_script="uncompyle_6.py" # 默认使用uncompyle6
    print("当前使用 uncompyle6 库")
if "--uncompyle6" in sys.argv:
    sys.argv.remove("--uncompyle6")

home=os.path.split("__file__")[0]
temp_path="_temp_decompiler"
empty_code=compile('','','exec').co_code # 空的字节码
for file in sys.argv[1:]:
    print("处理:",file)
    path,filename=os.path.split(file)
    fname,ext=os.path.splitext(filename)
    os.makedirs(os.path.join(path,temp_path),exist_ok=True)

    with open(file,"rb") as f:
        if f.read(4)!=MAGIC_NUMBER:
            warn("pyc文件版本可能和当前python版本不匹配")
    c=Code.from_pycfile(file)
    # 预处理pyc文件，分离出函数和类的字节码
    original_code=[]
    lst=[]
    for i in range(len(c.co_consts)):
        value=c.co_consts[i]
        if isinstance(value,CodeType):
            original_code.append(value)
            co=Code(value)
            co.co_code=empty_code # 直接返回一个值
            co.co_consts=(i,)
            lst.append(co.to_code())
        else:
            lst.append(value)
    c.co_consts=tuple(lst)
    c.co_lnotab=b''
    c.co_firstlineno=1
    preprocessed=os.path.join(path,temp_path,fname+"_preprocessed.pyc")
    preprocessed_py=os.path.join(path,temp_path,fname+"_preprocessed.py")
    c.to_pycfile(preprocessed)
    subprocess.run([sys.executable,os.path.join(home,decomp_script),preprocessed])

    max_parallel=os.cpu_count() # 最大进程数量
    processes=[];completed=failed=0;
    print("主模块反编译完成，正在反编译函数和类，最大进程数: %d"%max_parallel)
    for co in original_code:
        _wait_process(processes,max_parallel) # 等待多余进程结束
        # 反编译函数和类的字节码
        filename=os.path.join(path,temp_path,co.co_name+".pyc")
        print("正在反编译函数或类 %s 字节码长度: %d" %(
                co.co_name,len(co.co_code)))
        Code(co).to_pycfile(filename)
        proc=subprocess.Popen([sys.executable,
                               os.path.join(home,decomp_script),filename])
        processes.append(proc)

    _wait_process(processes,0) # 等待剩下的进程

    output=os.path.join(path,fname+".py")
    # 最后合并函数、类的反编译结果
    result=subprocess.run([sys.executable,
                           os.path.join(home,"decompile_merger.py"),
                           preprocessed_py,output])
    if result.returncode==0:
        print("文件 %s 反编译完成, %d/%d 个函数或类反编译失败\n"%(
                file,failed,len(original_code)))
    else:
        print("文件 %s 合并失败\n"%file)