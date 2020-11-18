cd
改变目录
cd /
cd ..回到上一级目录
cd ../../回到上两级目录

ls：查看当前目录的文件
ls -a: 全部文件，与隐藏文件（开头为.的文件）
ls -l：全部文件，与隐藏文件，但不包括.与..这两个目录
-d:仅列出目录本身，而不是列出目录内的文件数据
-f: 直接列出结果，不进行排序

pwd 显示当前目录

mkdir new_folder：新建文件夹
touch a.txt：新建文件
vi a.txt
cat a.txt  查看文件
tail a.txt
cp a.txt b.txt ：做一个拷贝文件b,在当前目录
cp a.txt /tmp  :复制到/tmp文件加下
mv a.txt c.txt :重命名
mv c.txt /tmp: 剪切复制
rm a.txt :删除文件
echo 'hello' > a.txt :快速写入文件
rmdir newfolder :删除文件夹，必须保证此文件夹为空
rm -rf newfolser :删除文件夹及文件夹下所有东西
clear:

cd --help: 打开cd对应的帮助文档

top ：查看进程

sh

