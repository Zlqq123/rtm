import sys
'''
given input_input and steps,output hist.
input_data:list,steps:[start,step,end]
output:dictionary, key:start of every block
value: stastics result
'''

#input_data is continuous variable
#interval1 is for input_data1
def hist_con(input_data,steps):
    if not input_data:
        print('Input_data is empty')
        sys.exit(1)
    result={}
    for i in range(len(steps)-1):
        block=str(steps[i])+'~'+str(steps[i+1])
        result[block]=0
        for value in input_data:
            if value>=steps[i] and value<steps[i+1]:
                result[block]=result.get(block,0)+1
    keys=[]
    values=[]
    for k in result.keys():
        keys.append(k)
        values.append(result[k])

    return keys,values

#input_data1 is continuous variable
#input_data2 is Discrete variable
#interval1 is for input_data1
def hist_con_dis(input_data1,input_data2,interval1):
    result=[]
    n=len(interval1)-1
    res1=[]
    for i in range(n):
        block=str(interval1[i])+'~'+str(interval1[i+1])
        result.append(block)
        dic={}
        for k in (range(len(input_data1))):
            value1=input_data1[k]
            value2=input_data2[k]
            if value1>=interval1[i] and value1<interval1[i+1]:
                dic[value2]=dic.get(value2,0)+1
        res1.append(dic)

    return result,res1

#input_data1 is continuous variable
#input_data2 is continuous variable
#interval1 is for input_data1
#interval2 is for input_data1
def hist_2con(input_data1,interval1,input_data2,interval2):
    l1=len(interval1)-1
    l2=len(interval2)-1
    res=[]
    interval_list1=[]
    interval_list2=[]
    for j in range(l2):
        interval_list2.append(str(interval2[j])+'~'+str(interval2[j+1]))

    for i in range(l1):
        interval_list1.append(str(interval1[i])+'~'+str(interval1[i+1]))
        res.append([])
        for j in range(l2):
            pp=0
            for k in (range(len(input_data1))):
                value1=input_data1[k]
                value2=input_data2[k]                
                if value1>=interval1[i] and value1<interval1[i+1] and value2>=interval2[j] and value2<interval2[j+1]:
                    pp+=1
            res[i].append(pp)
    return interval_list1,interval_list2,res



#def hist(input_data,steps):
#    if not input_data:
#        print('Input_data is empty')
#        sys.exit(1)
#    result={}
#
#    for i in range(steps[0],steps[2],steps[1]):
#        block=str(i)+'~'+str(i+steps[1])
#        result[block]=0
#        for value in input_data:
#            if value>=i and value<i+steps[1]:
#                result[block]=result.get(block,0)+1
#    keys=[]
#    values=[]
#    for k in result.keys():
#        keys.append(k)
#        values.append(result[k])
#
#    return keys,values