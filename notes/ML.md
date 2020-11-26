## 机器学习评价指标

ROC曲线全称为受试者工作特征曲线 （receiver operating characteristic curve），它是根据一系列不同的二分类方式（分界值或决定阈），以真阳性率（敏感性）为纵坐标，假阳性率（1-特异性）为横坐标绘制的曲线
AUC就是衡量学习器优劣的一种性能指标。从定义可知，AUC可通过对ROC曲线下各部分的面积求和而得。
ROC曲线的横坐标是伪阳性率（也叫假正类率，False Positive Rate），纵坐标是真阳性率（真正类率，True Positive Rate），相应的还有真阴性率（真负类率，True Negative Rate）和伪阴性率（假负类率，False Negative Rate）。这四类指标的计算方法如下：
　　（1）伪阳性率（FPR）：判定为正例却不是真正例的概率，即真负例中判为正例的概率
　　（2）真阳性率（TPR）：判定为正例也是真正例的概率，即真正例中判为正例的概率（也即正例召回率）
　　（3）伪阴性率（FNR）：判定为负例却不是真负例的概率，即真正例中判为负例的概率。
（4）真阴性率（TNR）：判定为负例也是真负例的概率，即真负例中判为负例的概率。
ROC（Receiver Operating Characteristic）曲线，又称接受者操作特征曲线。该曲线最早应用于雷达信号检测领域，用于区分信号与噪声。后来人们将其用于评价模型的预测能力，ROC曲线是基于混淆矩阵得出的。一个二分类模型的阈值可能设定为高或低，每种阈值的设定会得出不同的 FPR 和 TPR ，将同一模型每个阈值的 (FPR, TPR) 坐标都画在 ROC 空间里，就成为特定模型的ROC曲线。ROC曲线横坐标为假正率（FPR），纵坐标为真正率（TPR）。
AUC就是曲线下面积，在比较不同的分类模型时，可以将每个模型的ROC曲线都画出来，比较曲线下面积做为模型优劣的指标。ROC 曲线下方的面积(Area under the Curve)，其意义是：
（1）因为是在1x1的方格里求面积，AUC必在0~1之间。
（2）假设阈值以上是阳性，以下是阴性；
（3）若随机抽取一个阳性样本和一个阴性样本，分类器正确判断阳性样本的值高于阴性样本的概率 = AUC 。
（4）简单说：AUC值越大的分类器，正确率越高。
从AUC 判断分类器（预测模型）优劣的标准：
AUC = 1，是完美分类器。
AUC = [0.85, 0.95], 效果很好
AUC = [0.7, 0.85], 效果一般
AUC = [0.5, 0.7],效果较低，但用于预测股票已经很不错了
AUC = 0.5，跟随机猜测一样（例：丢铜板），模型没有预测价值。
AUC < 0.5，比随机猜测还差；但只要总是反预测而行，就优于随机猜测

>>from sklearn.metrics import roc_curve,auc

>>fpr, tpr, thresholds = roc_curve(y_test_s, y_pred, pos_label=1)

>>roc_auc = auc(fpr, tpr)  ###计算auc的值

>>lw = 2
>>plt.figure(figsize=(8, 5))
>>plt.plot(fpr, tpr, color='darkorange', lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)  ###假正率为横坐标，真正率为纵坐标做曲线
>>plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
>>plt.grid()
>>plt.xlim([0.0, 1.0])
>>plt.ylim([0.0, 1.0])
>>plt.xlabel('False Positive Rate')
>>plt.ylabel('True Positive Rate')
>>plt.title('Receiver operating characteristic example')
>>plt.legend(loc="lower right")
>>plt.show()


## 解决样本类别分布不均衡的问题

### 定义
所谓的不平衡指的是不同类别的样本量异非常大。样本类别分布不平衡主要出现在分类相关的建模问题上。样本类别分布不均衡从数据规模上可以分为大数据分布不均衡和小数据分布不均衡两种。

#### 大数据分布不均衡
这种情况下整体数据规模大，只是其中的少样本类的占比较少。但是从每个特征的分布来看，小样本也覆盖了大部分或全部的特征。例如拥有1000万条记录的数据集中，其中占比50万条的少数分类样本便于属于这种情况。
#### 小数据分布不均衡
这种情况下整体数据规模小，并且占据少量样本比例的分类数量也少，这会导致特征分布的严重不平衡。例如拥有1000条数据样本的数据集中，其中占有10条样本的分类，其特征无论如何拟合也无法实现完整特征值的覆盖，此时属于严重的数据样本分布不均衡。
样本分布不均衡将导致样本量少的分类所包含的特征过少，并很难从中提取规律；即使得到分类模型，也容易产生过度依赖于有限的数据样本而导致过拟合的问题，当模型应用到新的数据上时，模型的准确性和鲁棒性将很差。

样本分布不平衡主要在于不同类别间的样本比例差异，以笔者的工作经验看，如果不同分类间的样本量差异达到超过10倍就需要引起警觉并考虑处理该问题，超过20倍就要一定要解决该问题。

### 常见发生场景
在数据化运营过程中，以下场景会经常产生样本分布不均衡的问题：

#### 异常检测场景。
大多数企业中的异常个案都是少量的，比如恶意刷单、黄牛订单、信用卡欺诈、电力窃电、设备故障等，这些数据样本所占的比例通常是整体样本中很少的一部分，以信用卡欺诈为例，刷实体信用卡的欺诈比例一般都在0.1%以内。
#### 客户流失场景。
大型企业的流失客户相对于整体客户通常是少量的，尤其对于具有垄断地位的行业巨擘，例如电信、石油、网络运营商等更是如此。
#### 罕见事件的分析。
罕见事件与异常检测类似，都属于发生个案较少；但不同点在于异常检测通常都有是预先定义好的规则和逻辑，并且大多数异常事件都对会企业运营造成负面影响，因此针对异常事件的检测和预防非常重要；但罕见事件则无法预判，并且也没有明显的积极和消极影响倾向。例如由于某网络大V无意中转发了企业的一条趣味广告导致用户流量明显提升便属于此类。
#### 发生频率低的事件。
这种事件是预期或计划性事件，但是发生频率非常低。例如每年1次的双11盛会一般都会产生较高的销售额，但放到全年来看这一天的销售额占比很可能只有1%不到，尤其对于很少参与活动的公司而言，这种情况更加明显。这种属于典型的低频事件。

### 解决方法
#### 过抽样
过抽样（也叫上采样、over-sampling）方法通过增加分类中少数类样本的数量来实现样本均衡，最直接的方法是简单复制少数类样本形成多条记录，这种方法的缺点是如果样本特征少而可能导致过拟合的问题；经过改进的过抽样方法通过在少数类中加入随机噪声、干扰数据或通过一定规则产生新的合成样本，例如SMOTE算法。
#### 欠抽样
欠抽样（也叫下采样、under-sampling）方法通过减少分类中多数类样本的样本数量来实现样本均衡，最直接的方法是随机地去掉一些多数类样本来减小多数类的规模，缺点是会丢失多数类样本中的一些重要信息。

总体上，过抽样和欠抽样更适合大数据分布不均衡的情况，尤其是第一种（过抽样）方法应用更加广泛。

#### 正负样本的惩罚权重解决样本不均衡
通过正负样本的惩罚权重解决样本不均衡的问题的思想是在算法实现过程中，对于分类中不同样本数量的类别分别赋予不同的权重（一般思路分类中的小样本量类别权重高，大样本量类别权重低），然后进行计算和建模。

使用这种方法时需要对样本本身做额外处理，只需在算法模型的参数中进行相应设置即可。很多模型和算法中都有基于类别参数的调整设置，以scikit-learn中的SVM为例，通过在class_weight: {dict, ‘balanced’}中针对不同类别针对不同的权重，来手动指定不同类别的权重。如果使用其默认的方法balanced，那么SVM会将权重设置为与不同类别样本数量呈反比的权重来做自动均衡处理，计算公式为：n_samples / (n_classes * np.bincount(y))。

如果算法本身支持，这种思路是更加简单且高效的方法。

#### 通过组合/集成方法解决样本不均衡
组合/集成方法指的是在每次生成训练集时使用所有分类中的小样本量，同时从分类中的大样本量中随机抽取数据来与小样本量合并构成训练集，这样反复多次会得到很多训练集和训练模型。最后在应用时，使用组合方法（例如投票、加权投票等）产生分类预测结果。

例如，在数据集中的正、负例的样本分别为100和10000条，比例为1:100。此时可以将负例样本（类别中的大量样本集）随机分为100份（当然也可以分更多），每份100条数据；然后每次形成训练集时使用所有的正样本（100条）和随机抽取的负样本（100条）形成新的数据集。如此反复可以得到100个训练集和对应的训练模型。

这种解决问题的思路类似于随机森林。在随机森林中，虽然每个小决策树的分类能力很弱，但是通过大量的“小树”组合形成的“森林”具有良好的模型预测能力。

如果计算资源充足，并且对于模型的时效性要求不高的话，这种方法比较合适。

#### 通过特征选择解决样本不均衡
上述几种方法都是基于数据行的操作，通过多种途径来使得不同类别的样本数据行记录均衡。除此以外，还可以考虑使用或辅助于基于列的特征选择方法。

一般情况下，样本不均衡也会导致特征分布不均衡，但如果小类别样本量具有一定的规模，那么意味着其特征值的分布较为均匀，可通过选择具有显著型的特征配合参与解决样本不均衡问题，也能在一定程度上提高模型效果。

提示 上述几种方法的思路都是基于分类问题解决的。实际上，这种从大规模数据中寻找罕见数据的情况，也可以使用非监督式的学习方法，例如使用One-class SVM进行异常检测。分类是监督式方法，前期是基于带有标签（Label）的数据进行分类预测；而采用非监督式方法，则是使用除了标签以外的其他特征进行模型拟合，这样也能得到异常数据记录。所以，要解决异常检测类的问题，先是考虑整体思路，然后再考虑方法模型。

### 代码实操：Python处理样本不均衡
本示例中，我们主要使用一个新的专门用于不平衡数据处理的Python包imbalanced-learn，读者需要先在系统终端的命令行使用pip install imbalanced-learn进行安装；安装成功后，在Python或IPython命令行窗口通过使用import imblearn（注意导入的库名）检查安装是否正确，示例代码包版本为0.2.1。除此以外，我们还会使用sklearn的SVM在算法中通过调整类别权重来处理样本不均衡问题。本示例使用的数据源文件data2.txt位于“附件-chapter3”中，默认工作目录为“附件-chapter3”（如果不是，请cd切换到该目录下，否则会报“IOError: File data2.txt does not exist”）。完整代码如下：


>>import pandas as pd
from imblearn.over_sampling import SMOTE # 过抽样处理库SMOTE
from imblearn.under_sampling import RandomUnderSampler # 欠抽样处理库RandomUnderSampler
from sklearn.svm import SVC #SVM中的分类算法SVC
from imblearn.ensemble import EasyEnsemble # 简单集成方法EasyEnsemble

#导入数据文件
df = pd.read_table('data2.txt', sep=' ', names=['col1', 'col2','col3', 'col4', 'col5', 'label']) # 读取数据文件
x = df.iloc[:, :-1] # 切片，得到输入x
y = df.iloc[:, -1] # 切片，得到标签y
groupby_data_orgianl = df.groupby('label').count() # 对label做分类汇总
print (groupby_data_orgianl) # 打印输出原始数据集样本分类分布

#使用SMOTE方法进行过抽样处理
model_smote = SMOTE() # 建立SMOTE模型对象
x_smote_resampled, y_smote_resampled = model_smote.fit_sample(x,y) # 输入数据并作过抽样处理
x_smote_resampled = pd.DataFrame(x_smote_resampled, columns=['col1','col2', 'col3', 'col4', 'col5']) # 将数据转换为数据框并命名列名
y_smote_resampled = pd.DataFrame(y_smote_resampled,columns=['label']) # 将数据转换为数据框并命名列名
smote_resampled = pd.concat([x_smote_resampled, y_smote_resampled],axis=1) # 按列合并数据框
groupby_data_smote = smote_resampled.groupby('label').count() # 对label做分类汇总
print (groupby_data_smote) # 打印输出经过SMOTE处理后的数据集样本分类分布

#使用RandomUnderSampler方法进行欠抽样处理
model_RandomUnderSampler = RandomUnderSampler() # 建立RandomUnderSampler模型对象
x_RandomUnderSampler_resampled, y_RandomUnderSampler_resampled =model_RandomUnderSampler.fit_sample(x,y) # 输入数据并作欠抽样处理
x_RandomUnderSampler_resampled =pd.DataFrame(x_RandomUnderSampler_resampled,columns=['col1','col2','col3','col4','col5'])
#将数据转换为数据框并命名列名
y_RandomUnderSampler_resampled =pd.DataFrame(y_RandomUnderSampler_resampled,columns=['label']) # 将数据转换为数据框并命名列名
RandomUnderSampler_resampled =pd.concat([x_RandomUnderSampler_resampled, y_RandomUnderSampler_resampled], axis= 1) # 按列合并数据框
groupby_data_RandomUnderSampler =RandomUnderSampler_resampled.groupby('label').count() # 对label做分类汇总
print (groupby_data_RandomUnderSampler) # 打印输出经过RandomUnderSampler处理后的数据集样本分类分布

#使用SVM的权重调节处理不均衡样本
model_svm = SVC(class_weight='balanced') # 创建SVC模型对象并指定类别权重
model_svm.fit(x, y) # 输入x和y并训练模型

#使用集成方法EasyEnsemble处理不均衡样本
model_EasyEnsemble = EasyEnsemble() # 建立EasyEnsemble模型对象
x_EasyEnsemble_resampled, y_EasyEnsemble_resampled =
model_EasyEnsemble.fit_sample(x, y) # 输入数据并应用集成方法处理
print (x_EasyEnsemble_resampled.shape) # 打印输出集成方法处理后的x样本集概况
print (y_EasyEnsemble_resampled.shape) # 打印输出集成方法处理后的y标签集概况

#抽取其中一份数据做审查
index_num = 1 # 设置抽样样本集索引
x_EasyEnsemble_resampled_t =pd.DataFrame(x_EasyEnsemble_resampled[index_num],columns=['col1','col2','col3','col4','col5'])
#将数据转换为数据框并命名列名
y_EasyEnsemble_resampled_t =pd.DataFrame(y_EasyEnsemble_resampled[index_num],columns=['label']) # 将数据转换为数据框并命名列名
EasyEnsemble_resampled = pd.concat([x_EasyEnsemble_resampled_t,
y_EasyEnsemble_resampled_t], axis = 1) # 按列合并数据框
groupby_data_EasyEnsemble =EasyEnsemble_resampled.groupby('label').count() # 对label做分类汇总
print (groupby_data_EasyEnsemble) # 打印输出经过EasyEnsemble处理后的数据集样本分类分布
示例代码以空行分为6部分。

第一部分导入库。本示例中用到了第三方库imbalanced-learn实现主要的样本不均衡处理，而pandas的引入主要用于解释和说明不同处理方法得到的结果集样本的分布情况，sklearn.svm中的SVC主要用于说明SVM如何在算法中自动调整分类权重。

第二部分导入数据文件。该过程中使用pandas的read_table读取本地文件，为了更好的区别不同的列，通过names指定列名；对数据框做切片分割得到输入的x和目标变量y；通过pandas的groupby()方法按照label类做分类汇总，汇总方式是使用count()函数计数。输入原始数据集样本分类分布如下：

col1 col2 col3 col4 col5
label 
0.0 942 942 942 942 942
1.0 58 58 58 58 58
输出结果显示了原始数据集中，正样本（label为1）的数量仅有58个，占总样本量的5.8%，属于严重不均衡分布。

第三部分使用SMOTE方法进行过抽样处理。该过程中首先建立SMOTE模型对象，并直接应用fit_sample对数据进行过抽样处理，如果要获得有关smote的具体参数信息，可先使用fit(x,y)方法获得模型信息，并得到模型不同参数和属性；从fit_sample方法分别得到对x和y过抽样处理后的数据集，将两份数据集转换为数据框然后合并为一个整体数据框；最后通过pandas提供的groupby()方法按照label类做分类汇总，汇总方式是使用count()函数计数。经过SMOTE处理后的数据集样本分类分布如下：

col1 col2 col3 col4 col5
label 
0.0 942 942 942 942 942
1.0 942 942 942 942 942
通过对比第二部分代码段的原始数据集返回结果发现，该结果中的正样本（label为1）的数量增加，并与负样本数量相同，均为942条，数据分类样本得到平衡。

第四部分使用RandomUnderSampler方法进行欠抽样处理。该过程与第三部分步骤完全相同，在此略过各模块介绍，用途都已在代码备注中注明。经过RandomUnderSampler处理后的数据集样本分类分布如下：

col1 col2 col3 col4 col5
label 
0.0 58 58 58 58 58
1.0 58 58 58 58 58
通过对比第二部分代码段的原始数据集返回的结果，该结果中的负样本（label为0）的数量减少，并跟正样本相同，均为58条，样本得到平衡。

第五部分使用SVM的权重调节处理不均衡样本。该过程主要通过配置SVC中的class_weight参数和值的设置来处理样本权重，该参数可设置为字典、None或字符串balanced三种模式：

字典：通过手动指定的不同类别的权重，例如{1:10,0:1}
None：代表类别的权重相同
balanced：代表算法将自动调整与输入数据中的类频率成反比的权重，具体公式为n_samples /（n_classes * np.bincount（y）），程序示例中使用了该方法
经过设置后，算法自动处理样本分类权重，无需用户做其他处理。要对新的数据集做预测，只需要调用model_svm模型对象的predict方法即可。

第六部分使用集成方法EasyEnsemble处理不均衡样本。该方法的主要过程与其他imblearn方法过程类似，不同点在于集成方法返回的数据为三维数据，即将数据在原来的基础上新增了一个维度——“份数”，集成方法返回的数据x和y的形状为(10, 116, 5)和(10, 116)。为了更详细的查看其中每一份数据，抽取其中一份数据做审查，得到的每份数据返回结果如下：

col1 col2 col3 col4 col5
label 
0.0 58 58 58 58 58
1.0 58 58 58 58 58
通过对比第二部分代码段的原始数据集返回的结果，该结果中的负样本（label为0）的数量减少，并跟正样本相同，均为58条，样本集得到平衡。随后的应用中，可以通过循环读取每一份数据训练模型并得到结果，然后将10（x处理后返回的结果，通过形状名年龄返回的元组中的第一个数值，x_EasyEnsemble_resampled.shape[0]）份数据的结果通过一定方法做汇总。

上述过程中，主要需要考虑的关键点是：

如何针对不同的具体场景选择最合适的样本均衡解决方案，选择过程中既要考虑到每个类别样本的分布情况以及总样本情况，又要考虑后续数据建模算法的适应性，以及整个数据模型计算的数据时效性。

代码实操小结：本小节示例中，主要用了几个知识点：

通过pandas的read_table方法读取文本数据文件，并指定列名
对数据框做切片处理
通过pandas提供的groupby()方法配合count()做分类汇总
使用imblearn.over_sampling中的SMOTE做过抽样处理
使用imblearn.under_sampling中的RandomUnderSampler做欠抽样处理
使用imblearn.ensemble中的EasyEnsemble做集成处理
使用sklearn.svm 中的SVC自动调整算法对不同类别的权重设置
提示 第三方库imblearn提供了非常多的样本不均衡处理方法，限于篇幅无法做一一介绍，建议读者自行安装并学习和了解不同的用法。