import sys,os,traceback
import uncompyle6.bin.uncompile as decompiler
__version__='2.0.1'

def run_uncompile(filename):
    # 截获sys.stderr中的警告和错误消息
    message=""
    _write=sys.stderr.write
    def write(text,*arg,**kw):
        nonlocal message
        message+=text # 截获消息
        #_write(text,*arg,**kw)
    def start_capture(): # 开始监测,修改sys.stderr.write方法
        sys.stderr.write=write
    def end_capture():  # 停止监测
        sys.stderr.write=_write

    tofilename=filename[:-1]
    try:
        sys.stdout=open(tofilename,"w",encoding="utf-8") # 替换sys.stdout
        sys.argv[1]=filename
        start_capture()
        try:decompiler.main_bin() # 运行反编译
        except SystemExit:
            pass
    except KeyboardInterrupt:
        end_capture()
        return 3
    except Exception:
        end_capture()
        traceback.print_exc(file=sys.stdout)
        return 2
    else:
        end_capture()
        if not message:
            return 0
        else:
            sys.stdout.write(message)
            return 1
    finally:
        sys.stdout.close()

if __name__=="__main__":
    try:
        if len(sys.argv)>1:
            files=sys.argv[1:]
            sys.argv[0]=decompiler.__file__
            sys.argv[1:]=['']
            retcodes=[]
            for file in files:
                retcodes.append(run_uncompile(file))
            retcode=max(retcodes) # 取最严重的错误
        else:
            file=input("拖曳文件到本窗口,然后按回车:\n").strip('"')
            sys.argv[0]=decompiler.__file__
            sys.argv.append('')
            retcode=run_uncompile(file)
    finally:
        sys.stdout=sys.__stdout__

    sys.exit(retcode)
