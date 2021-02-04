
## MySQL
### 
SQL 语句不区分大小写，所有语句以;结尾

语法描述项
<>：表示在语句中必须指定的数据对象， 是不可缺少
[]：表示可以根据需要进行选择，也可以不选
|：表示多个选项只能择其一，
{}：表示必选项

语句分类：
DDL (Data Deginition Language)  create drop alter
DML (Data Manipulation laanguage) insert,delete update select 
DCL (Data Control Languange) grant revoke

### 数据库操作
#### create
CREATE Database [IF NOT EXISTS] <Db_name> 
[[DEFAULT] CHARACTER SET <字符集> | [DEFAULT] COLLATE <校对规则名>]
指定字符集（utf8....)

#### SHOW
SHOW DATABASES [LIKE <数据库名>]

#### ALTER 修改
ALTER DATABASE [db_name]
{[DEFAULT] CHARACTER SET <字符集>}

#### DROP
DROP DATABASE [IF EXISTS] <DB_name>

### table
#### create
create table [IF NOT EXISTS] <tb_name>
(col1  type,col2  type,......
primary key (col) #指定主键
)


create tabele tb_name like tb_name1 #同结构的表复制，只复制结构，不复制数据

SELECT a.id FROM Weather as a INNER JOIN Wheather as b
Where DATEDIFF(a.recordDaye, b.recordDate)=1 AND a.temperatue > b.temperature
查询温度比前一天温度高的所有日期ID
 
order by rand() 按照随机顺序


DROP TABLE IF EXISTS t_company;
CREATE TABLE IF NOT EXISTS t_company (
id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '公司ID', code VARCHAR (10) NOT NULL COMMENT '公司编码',
short_name VARCHAR (10) NOT NULL COMMENT '公司简称', full_name VARCHAR (20) NOT NULL COMMENT '公司全称',
address VARCHAR (100) COMMENT '公司详细地址', create_date date NOT NULL COMMENT '成立日期',
PRIMARY KEY (id)
) ENGINE=INNODB DEFAULT CHARSET=utf8;


drop table if exists t_car;
create table if not exists t_car(
id bigint not null auto_increment,
brand_name varchar(20) COMMENT '品牌名称',
model_name varchar(20) COMMENT '型号名称',
color INT COMMENT '颜色',
height float(10,2) COMMENT '高度',
width double(10,2) COMMENT '宽度',
weight decimal(10,2) COMMENT '重量',
factory_no varchar(10) COMMENT '出厂编号',
company_id BIGINT UNSIGNED COMMENT '公司ID',
product_date date COMMENT '生产日期',
start_time datetime COMMENT '组装开始时间',
end_time datetime COMMENT '组装结束时间',
employee_id BIGINT UNSIGNED COMMENT '员工ID',
foreign key (company_id) REFERENCES t_company(id),
foreign key (employee_id) REFERENCES t_employee(id),   #指定外键
primary key(id)  
) ENGINE=INNODB DEFAULT CHARSET=utf8;



#### 查看表结构
desc tb_name

#### insert into
Insert into tb_name (col1, col2, col3) values (v1,v2,v3)

#### delete
delete from tb_name [WHERE expr]

#### select


#### update
update tb_name set 

#### where epr
like '%sh%'#字符里面含sh %是通配符

like 'sh__'#字符是shxx,后面正好只有两位
 
=  与  <=>

非 NOT !

且 AND &&

或 OR ||

异或 XOR

### 数据类型
整形：

| type | storage(bytes) | min~max (sigend) |min~max(unsigned)
| :------:| :------: | :----------: | :----------: |
| TINYINT | 1 | -128~127 | 0~255 |
| SMALLINT | 2 | -32768~32768 | 0~65535 |
| MEDIUMT | 3 | -2e15~2e15-1 | 0~2e16-1 |
| int | 4 | -2e31~2e31-1 | 0~2e32-1 |
| bigint | 5 | -2e63~2e63-1 | 0~2e64-1 |

时间日期：
| type | storage(bytes) | min~max (sigend) | zero value | formate |
| :------:| :------: | :-----------------: | :-----------: | :-----------: |
| YEAR | 1 | 1901~2155 |  |  |  |
| TIME | 3 | -838:59:59 ~ 838:59:59 |  |  |  |
| DATE | 3 | 1000-01-01~9999-12-31 |  |  |  |
| DATETIME | 8 | 1000-01-01 00:00:00 ~9999-12-31 23:59:59  |  |  |  |
| TIMESTAMP | 4 | 1901~2155 UTC | UTC |  |  |



### 权限管理
create user 'kevin'@'localhost' identified by '123456';
创建角色权限
grant insert,select,create on  <databasename.tbname>dbcar. * to 'kevin'@'%';

revoke all on dbcar. * from 'kevin'@'%';
删除权限
show grants for 'kevin'@'%';
显示用户的所有权限
flush pr
设置权限立即生效

drop user 
删除用户

select * from mysql.'user';
查看数据库的所有用户

### 联合查询：
SELECT tb1.colx, tb2.coly 
FROM tb1,tb2 WHERE tb1.colz=tb2.colw


SELECT 列1，列2，列3....
FROM 表1
INNER JOIN 表2 on 表1.列x=表2.列y 
WHERE  表1.列4 > xx  and 表2.列5 > xx and  ......



SELECT 列1，列2，列3....
FROM 表1
WHERE 表1.列x in ( SELECT 列y from 表2 where 表2.列5 > xx )
and  表1.列4 > xx  and......


### 函数

#### 聚合函数
count sum max min avg

select col1, count(*) from t_car group by col1

select col1, sum(col2) from tb group by col1 order by sum(col2) desc

select col1, sum(col2) from tb group by col1 
HAVING sum(col2)>20


SELECT * FROM TB_NAME ORDER BY col1 DESC LIMIT 10,10
#选取col1中第10名到第20 名

SELECT * FROM TB_NAME WHERE col1=(select max(col1) from tb_name)


#### 字符串函数
left
right
mid
substring
contract
contract_ws()
trim()
insert()
#### 数值函数


## clickhouse in python
from clickhouse_driver import Client

client=Client(host='xx.xxx.xx.xx',port='xxxx',user='xxxx' ,password='xxxx',database='xxxx')

sql="desc en.rtm_vds"

aus=client.execute(sql)

### Clause
#### desc 
查看表结构
>>desc en.rtm_6_2th

#### SELECT
[WITH expr_list|(subquery)]

SELECT [DISTINCT] expr_list

[FROM [db.]table | (subquery) | table_function] [FINAL]

[SAMPLE sample_coeff]

[ARRAY JOIN ...]

[GLOBAL] [ANY|ALL] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER] JOIN (subquery)|table USING columns_list

[PREWHERE expr]

[WHERE expr]

[GROUP BY expr_list] [WITH TOTALS]

[HAVING expr]

[ORDER BY expr_list]

[LIMIT [offset_value, ]n BY columns]

[LIMIT [n, ]m]

[UNION ALL ...]

[INTO OUTFILE filename]

[FORMAT format]

>>select * from en.rtm_vds limit 10 #选取前十条记录

#### with
变量1 as 别名 将变量1命名为别名

#### distinct uniq
select count(distinct deviceid) from en.rtm_vds

select uniq(deviceid) from en.rtm_vds

输出车辆个数，上面两个表述等价

### data structure

#### str
lower, lcase

Converts ASCII Latin symbols in a string to lowercase.

upper, ucase

Converts ASCII Latin symbols in a string to uppercase.

concat

Concatenates the strings listed in the arguments, without a separator.

concat(s1, s2, ...)

substring(s, offset, length), mid(s, offset, length), substr(s, offset,length)

Returns a substring starting with the byte from the ‘offset’ index that is ‘length’ bytes long. Character

##### like 模糊匹配

Checks whether a string matches a simple regular expression.

The regular expression can contain the metasymbols % and _.

% indicates any quantity of any bytes (including zero characters).

_ indicates any one byte.

Use the backslash (\) for escaping metasymbols. See the note on escaping in the description of the ‘match’ function.

>>select distinct deviceid from en.rtm_vds where deviceid like 'LSVA%' #从 "deviceid" 列中仅选取唯一不同的值,条件是"deviceid"以LSVA开头

##### string <-> Array
splitByChar(separator, s)

Splits a string into substrings separated by a specified character. It uses a constant string separator which consisting of exactly one character.

Returns an array of selected substrings. Empty substrings may be selected if the separator occurs at the beginning or end of the string, or if there are multiple consecutive separators.

splitByChar(',',字符串)将字符串用','分割，得到一个字符串数组

splitByString(separator, s)

Splits a string into substrings separated by a string. It uses a constant string separator of multiple characters as theseparator. If the string separator is empty, it will split the string s into an array of single characters.

arrayStringConcat(arr[, separator])

Concatenates the strings listed in the array with the separator.’separator’ is an optional parameter: a constant string, set to an empty string by default.

Returns the string.

#### Array
arrayReduce('sum',整形/浮点类型数组)数组求和

#arrayReduce('max',整形/浮点类型数组)求数组中的最大值

#length(数组)求数组长度

#### Type Conversion Functions
toInt(8|16|32|64)

toInt8(expr) — Results in the Int8 data type.

toInt16(expr) — Results in the Int16 data type.

toInt32(expr) — Results in the Int32 data type.

toInt64(expr) — Results in the Int64 data type.

toInt(8|16|32|64)OrZero

It takes an argument of type String and tries to parse it into Int (8 | 16 | 32 | 64). If failed, returns 0.

toInt(8|16|32|64)OrNull

It takes an argument of type String and tries to parse it into Int (8 | 16 | 32 | 64). If failed, returns NULL.

toUInt(8|16|32|64)

Converts an input value to the UInt data type. This function family includes:

toUInt8(expr) — Results in the UInt8 data type.

toUInt16(expr) — Results in the UInt16 data type.

toUInt32(expr) — Results in the UInt32 data type.

toUInt64(expr) — Results in the UInt64 data type.

toFloat(32|64)

toFloat(32|64)OrZero

toFloat(32|64)OrNull

toDate

toDateOrZero

toDateOrNull

toDateTime

toDateTimeOrZero

toDateTimeOrNull

toDecimal(32|64|128)

Converts value to the Decimal data type


CAST(x, t)

Converts ‘x’ to the ‘t’ data type

>>cast(emspeed,'Float32') as sp
>>cast(字符串数组,'Array(Int8)')将字符串数组转化成整形数组

#### Datatime 
toDateTime('2016-06-15 23:00:00') AS time,

toDate(time) AS date_local,

toDate(time, 'Asia/Yekaterinburg') AS date_yekat,

toString(time, 'US/Samoa') AS time_samoa

toTimeZone

Convert time or date and time to the specified time zone.

toYear

Converts a date or date with time to a UInt16 number containing the year number (AD).

toQuarter

Converts a date or date with time to a UInt8 number containing the quarter number.

toMonth

Converts a date or date with time to a UInt8 number containing the month number (1-12).

toDayOfYear

Converts a date or date with time to a UInt16 number containing the number of the day of the year (1-366).

toDayOfMonth

Converts a date or date with time to a UInt8 number containing the number of the day of the month (1-31).

toDayOfWeek

Converts a date or date with time to a UInt8 number containing the number of the day of the week (Monday is 1,and Sunday is 7).

toHour

Converts a date with time to a UInt8 number containing the number of the hour in 24-hour time (0-23).

This function assumes that if clocks are moved ahead, it is by one hour and occurs at 2 a.m., and if clocks are moved back, it is by one hour and occurs at 3 a.m. (which is not always true – even in Moscow the clocks were twice changed at a different time).

toMinute

Converts a date with time to a UInt8 number containing the number of the minute of the hour (0-59).

toSecond

Converts a date with time to a UInt8 number containing the number of the second in the minute (0-59).

Leap seconds are not accounted for.

now

Accepts zero arguments and returns the current time at one of the moments of request execution.This function returns a constant, even if the request took a long time to complete.

today

Accepts zero arguments and returns the current date at one of the moments of request execution.
The same as ‘toDate(now())’.

yesterday

Accepts zero arguments and returns yesterday’s date at one of the moments of request execution.
The same as ‘today() - 1’.

dateDiff

Returns the difference between two Date or DateTime values.

Syntax

dateDiff('unit', startdate, enddate, [timezone])

>>SELECT uploadtime FROM en.rtm_6_2th WHERE deviceid='LSVAX60E0K2016511' AND uploadtime between toDateTime('2020-06-01 19:12:04') AND toDateTime('2020-06-02 14:12:95')ORDER BY uploadtime 
>>"select deviceid,min(uploadtime),max(uploadtime) from rtm_vds group by deviceid  选出每辆车记录结束时间
>>SELECT deviceid,toDate(uploadtime), min(CAST(accmiles,'float')), max(CAST(accmiles,'float')) from rtm_vds where deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 group by deviceid, toDate(uploadtime)"#每日行驶里程统计



### function
#### runningDifference
#第n行runningDifference(变量)=第n行变量值-第n-1行变量值

#runningDifference(变量) 需要在子查询中查询

#SLELCT 变量1，变量2.。。runningDifference(变量) from（SELECT 变量1，变量2.。。 FROM table ORDER BY 变量1，变量2）

>>SELECT deviceid,uploadtime,soc,runningDifference(soc) from (SELECT deviceid,uploadtime,soc from en.rtm_vds where cocesprotemp1!='NULL' ORDER BY deviceid,uploadtime)



### Conditional Expression
a ? b : c – The if(a, b, c) function.

SELECT if(cond, then, else)

multiIf

Allows you to write the CASE operator more compactly in the query.

Syntax: multiIf(cond_1, then_1, cond_2, then_2, ..., else)

CASE [x]

WHEN a THEN b

[WHEN ... THEN ...]

[ELSE c]

END

>>if(chargingstatus=='NO_CHARGING',7,8)

>>multiIf(P<-7.5,'DC',P>=-7.5 and P<-4,'mode3_1',P>=-4 and P<-2,'mode3_2',P>=-2 and P<0,'mode2','discharging')






### DROP
sql="DROP TABLE en.vehicle_vin"
#删除表

>>sql="INSERT INTO en.vehicle_vin (deviceid,project,city,province,region,user_typ) FORMAT Values ('LSVUZ60T1J2179379','Tiguan L PHEV C5','广州市','GuangDong','MidSouth','Private')"

#click house 没有update语句 没有delete


>>sql="Alter Table en.vehicle_vin DROP COLUMN d_mileage "

#删除列，只能一列一列的删除

### CREATE TABLE
CREATE TABLE [IF NOT EXISTS] [db.]table_name [ON CLUSTER cluster]

(

    name1 [type1] [DEFAULT|MATERIALIZED|ALIAS expr1] [TTL expr1],

    name2 [type2] [DEFAULT|MATERIALIZED|ALIAS expr2] [TTL expr2],

    ...

    INDEX index_name1 expr1 TYPE type1(...) GRANULARITY value1,

    INDEX index_name2 expr2 TYPE type2(...) GRANULARITY value2

) ENGINE = MergeTree()

ORDER BY expr

[PARTITION BY expr]

[PRIMARY KEY expr]

[SAMPLE BY expr]

[TTL expr [DELETE|TO DISK 'xxx'|TO VOLUME 'xxx'], ...]

[SETTINGS name=value, ...]

eg:
>>CREATE TABLE IF NOT EXISTS en.vehicle_vin ( deviceid String, project String, city String, province String, region String, mileage UInt32, user_type String ) ENGINE = MergeTree() ORDER BY deviceid #新建表，默认deviceid为主键

### ALTER TABLE
ALTER TABLE [db].name [ON CLUSTER cluster] ADD|DROP|CLEAR|COMMENT|MODIFY COLUMN ...

ADD COLUMN — Adds a new column to the table.

DROP COLUMN — Deletes the column.

CLEAR COLUMN — Resets column values.

COMMENT COLUMN — Adds a text comment to the column.

MODIFY COLUMN — Changes column’s type, default expression and TTL.

更新表
>>ALTER TABLE en.vehicle_vin ADD COLUMN user_typ String
>>ALTER TABLE en.vehicle_vin ADD COLUMN d_mile UInt32 AFTER mileage
