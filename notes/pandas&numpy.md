## Pandas

> import pandas as pd
>
> import numpy as np
>
> #df：任意的Pandas DataFrame对象    #s：任意的Pandas Series对象

### 创建及数据导入

> pd.DataFrame(np.random.rand(20,5))：创建20行5列的随机数组成的DataFrame对象
>

> df = pd.DataFrame(columns=['a_col', 'b_col',  'c_col'])#创建指定列的空dataframe

从list和dict中创建

> df=pd.DataFrame(data_list, columns=['a_col', 'b_col',  'c_col'])
>
> pd.Series(my_list) #从list创建一个Series对象
>
> df=pd.DataFrame(dict)#从字典对象导入数据，Key是列名，Value是数据

从CSV文件导入数据:

> df=pd.read_csv(filename,encoding="gbk",index_col=0,header=0)   #index_col=0声明文件第一列为索引    #header=0第一行为列名（默认就是，不必重新申明）

其他文件导入数据：

> df=pd.read_table(filename)     #从限定分隔符的文本文件导入数据
>
> pd.read_excel(filename,sheet_name=0)  #从Excel文件导入数据
>
> pd.read_sql(query, connection_object) #从SQL表/库导入数据
>
> pd.read_json(json_string)  #从JSON格式的字符串导入数据
>
> pd.read_html(url)     #解析URL、字符串或者HTML文件，抽取其中的tables表格
>
> pd.read_clipboard() #从你的粘贴板获取内容，并传给read_table()



### 导出数据

导出数据到CSV文件：

>df.to_csv(t_name,encoding="gbk",index=False)  #index=False不导出index
>

DataFrame转换成list    DataFrame转换成dict

> df.values.tolist()#生成list[[],[],[]...]
>
> df.to_dict('dict'/ 'list'/ 'series'/'split'/ 'records'/'index')
>
> ​      - 'dict' (default) : dict like {column -> {index -> value}}
>
> ​      \- 'list' : dict like {column -> [values]}
>
> ​      \- 'series' : dict like {column -> Series(values)}
>
> ​      \- 'split' : dict like             {'index' -> [index], 'columns' -> [columns], 'data' -> [values]}
>
> ​      \- 'records' : list like          [{column -> value}, ... , {column -> value}]
>
> ​      \- 'index' : dict like {index -> {column -> value}}

导出其他文件:

>df.to_excel(filename)   #导出数据到Excel文件
>
>df.to_sql(table_name, connection_object)  #导出数据到SQL表
>
>df.to_json(filename)  #以Json格式导出数据到文本文件



### 查看、检查数据

>df.head(n)：查看DataFrame对象的前n行
>
>df.tail(n)：查看DataFrame对象的最后n行
>
>df.shape()：查看行数和列数
>
>df.info()  #用于打印DataFrame的简要摘要，显示有关DataFrame的信息，包括索引的数据类型dtype和列的数据类型dtype，非空值的数量和内存使用情况。
>
>df.describe() #用于生成描述性统计信息。 描述性统计数据：数值类型的包括均值，标准差，最大值，最小值，分位数等；类别的包括个数，类别的数目，最高数量的类别及出现次数等；输出将根据提供的内容而有所不同。
>
>s.value_counts(dropna=False)：查看Series对象的唯一值和计数
>
>df.apply(pd.Series.value_counts)：查看DataFrame对象中每一列的唯一值和计数
>
>df.corr()：返回列与列之间的相关系数
>
>df.count()：返回每一列中的非空值的个数
>
>df.mean()    df.max()    df.min()  df.median()   df.std()   df.sum()   #返回每一列的平均值/最大值/最小值/中位数/标准差/求和
>
>#pandas中没有直接众数的计算，可转化为numpy后用np.mode()函数



###  数据选取

索引

.loc用于列名和行名索引，.iloc用于按照位置索引

>df[col]#根据列名，并以Series的形式返回列
>
>df[[col1, col2]]#以DataFrame形式返回多列
>
>s.iloc[0]#按位置选取数据
>
>s.loc['index_one']：按索引选取数据
>
>df.iloc[0,:]：返回第一行
>
>df.iloc[0,0]：返回第一列的第一个元素
>
>df.index = pd.date_range('1900/1/30', periods=df.shape[0])：增加一个日期索引

按照条件选取数据：

> index_s = K_line[K_line['date']>self.start_date].index[0] \#找到开始投资日期最近的开市日期,将k-line截取到从最近开市日开始

> K_line = K_line.iloc[index_s::,:]

> df[ df[col] > 0.5] #选择col列的值大于0.5的行

i = K_line[K_line['date']>s].index[0]

c = K_line.loc[K_line['date']==date]

pctChg=c.iloc[0,4]







### 数据清洗

#### 缺失值处理

查看缺失值

> df.isnull().sum() #查看每列数据缺失值个数
>
> df.isnull() #检查DataFrame对象中的空值，并返回一个Boolean数组
>
> df.notnull() #检查DataFrame对象中的非空值，并返回一个Boolean数组
>
> df.info() #打印DataFrame的简要摘要，显示有关DataFrame的信息，包括索引的数据类型dtype和列的数据类型dtype，非空值的数量和内存使用情况。

删除缺失值

> df.dropna()  #删除所有包含空值的行
>
> df.dropna(axis=1)  #删除所有包含空值的列
>
> df.dropna(axis=1,thresh=n)  #删除所有小于n个非空值的行
>
> df=df.dropna(subset=['a_col', 'b_col', 'c_col']) #删除abc三列中有缺失值的行

替换缺失值

> df=df.fillna('*')    #将所有丢失的数据替换为'*'
>
> df['a_col'] = df['a_col'].fillna(0)  #将某列丢失数据填充为0
>
> df['a_col'] = df['a_col'].fillna(df['a_col'].mean())  # 将某列丢失数据用该平均值代替





#### 行名&列名操作

重命名列名

> df.columns = ['a','b','c']

批量更改列名

>df.rename(columns=lambda x: x + 1)

选择性更改列名

>df.rename(columns={'old_name': 'new_ name'})

更改索引列

>df.set_index('column_one')

批量重命名索引

>df.rename(index=lambda x: x + 1)

> df = df.reset_index(drop=True)#index重新编号，原index删除



#### 数据替换

>s.replace([1,3],['one','three'])：用'one'代替1，用'three'代替3
>
>s.replace(1,'one')：用‘one’代替所有等于1的值



#### DataFrame 内部数据格式转换

将指定列object类型转化成数字类型

> df[['a_col', 'b_col']] = df[['a_col', 'b_col']].apply(pd.to_numeric)

 将指定列datetime类型数据转为str 以下二选一

> df["a_col"] = pd.to_datetime(df['a_col'])
>
> df["a_col"]=df["a_col"].apply(lambda x:datetime.datetime.strptime(x,'%Y-%m-%d'))

将Series中的数据类型更改为float类型

>s.astype(float)



#### 窗口函数rolling

> df['d_col'] = df['a_col'].rolling(window=5).mean() #创建新的一列，为a列前5行的平均值，后面的函数可以换成max,min,sum....
>



### DataFrame 拼接与合并

行拼接：

> df = df1.append(df2, ignore_index=True)  #在df1后加上df2
>
> df=pd.concat([df1, df2],axis=0)

列拼接：

> df=pd.concat([df1, df2],axis=1)   #df1 df2列拼接，拼接前需要保证df1 df2的index相同
>
> df1 = df1.reset_index(drop=True)    #index重新编号，旧index删除
>

对df1的列和df2的列执行SQL形式的join

>df1.join(df2,on=col1,how='inner')





### 数据处理：Filter、Sort和GroupBy

>df.sort_values(col1)    #按照列col1排序数据，默认升序排列
>
>df.sort_values(col2, ascending=False)    #按照列col1降序排列数据
>
>df.sort_values([col1,col2], ascending=[True,False])     #先按列col1升序排列，后按col2降序排列数据
>
>df.groupby(col)        #返回一个按列col进行分组的Groupby对象
>
>df.groupby([col1,col2])      #返回一个按多列进行分组的Groupby对象
>
>df.groupby(col1)[col2]        #返回按列col1进行分组后，列col2的均值
>
>df.pivot_table(index=col1, values=[col2,col3], aggfunc=max)      #创建一个按列col1进行分组，并计算col2和col3的最大值的数据透视表
>
>df.groupby(col1).agg(np.mean)     #返回按列col1分组的所有列的均值
>
>data.apply(np.mean)     #对DataFrame中的每一列应用函数np.mean
>
>data.apply(np.max,axis=1)    #对DataFrame中的每一行应用函数np.max



## numpy 
>t_aay = np.array([[1,2,3,4,1], [3,2,4,1,2]])
>np.sort(t_aay)
>np.argsort(t_aay)
t_aay.shape=2,5
t_aay.transpose()转置

拉平：
a.flatten()#对于原始数组不改变

数组连接：

> c=np.concatenate((a,b),axis=0)
> c=np.concatenate((a,b),axis=1)
> np.vstack((a,b))
> np.hstack((a,b))

构造数组
>np.zeros((3,2))
np.ones((3,5))
np.ones((3,5))*8
a=np.zeros_like(c) 创建预c矩阵一样大小的零矩阵
np.identity(5) 构造5*5的单位矩阵
>x=np.empty((3,2)) 慎用

np.random.rand(3,2)随机构造0~1的 float
nprandom.randint(n,size=(5,4)) 随机构造 [0,n) 的整数数组


mu,sigma=0,2
np.random.normal(mu,sigma,10)构造长度为10的数组，满足均值为0 ，方差为2的正太分布

洗牌
np.random.shuffle(a) 打乱数组a 的顺序
随机种子
np.random.seed(x)

## datetime

> import datetime

datatime创建，与str的互相转化

> date1 = datetime.date(2018, 10, 2) 
>
> s=date1.strftime('%Y-%m-%d')
>
> date2= datetime.datetime.strptime('2021-02-03', "%Y-%m-%d")

时间差函数

> date3=data1-datetime.timedelta(days=1)

判断是周几

> date1.isoweekday() #返回1~7对应周一~周日

判断是否是节假日/是否工作日

> import chinese_calendar
>
> demo_time = datetime.date(2018, 10, 2) 
>
> data_is_holiday = chinese_calendar.is_holiday(demo_time)  # True
>
> data_is_workday = chinese_calendar.is_workday(demo_time)  # False