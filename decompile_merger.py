import sys,os,re

TAB=" "*4
def indent(code):
    new_code = ""
    for line in code.splitlines():
        line=line.rstrip()
        if line:new_code+="\n"+TAB+line
        else:new_code+="\n"
    return new_code

if len(sys.argv)!=3:
    print("用法: python %s <要合并的.py文件名> <输出.py文件>" % sys.argv[0])
    sys.exit(1)
file,output=sys.argv[1:]

path,filename=os.path.split(file)
fname,ext=os.path.splitext(filename)
with open(file,"r",encoding="utf-8") as f:
    source_code=f.read()

functions_and_classes = re.findall(r'(def|class)\s([a-zA-Z0-9_]+)(.+)*:', source_code)
function_class_codes = []

for item in functions_and_classes:
    print("合并 %s %s%s:"%item)
    keyword, name, args = item
    file_name = os.path.join(path, name+".py") # 类、函数的.py文件需和待合并的.py文件在同一目录
    if os.path.exists(file_name):
        with open(file_name, 'r',encoding="utf-8") as file:
            function_class_code = file.read() + "\n"
            function_class_code = re.sub(r'^\s*#.*\n', '', function_class_code, flags=re.M) # 删除首尾的注释
            function_class_code = "%s %s%s:" % (keyword, name, args) + \
                                  indent(function_class_code)
            #function_class_codes.append(function_class_code)
            if args.strip():
                args=args.replace("\\","\\\\")
                args="\\(%s\\)" % args[1:-1]
                args=args.replace("*","\\*")
            function_class_code=function_class_code.replace("\\","\\\\")
            definition = "%s %s%s:" % (keyword, name, args)
            source_code=re.sub(definition+"\n(.*?)\n",function_class_code,source_code,
                               re.MULTILINE)
    else:print("文件名 %s 不存在"%file_name)

# 合并代码
#merged_code = '\n\n'.join(function_class_codes)
with open(output,"w",encoding="utf-8") as f:
    f.write(source_code)