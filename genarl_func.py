import sys
sys.path.append('./')
import time
import xlsxwriter

def print_in_excel(aus,s1):
    workbook = xlsxwriter.Workbook(s1)
    worksheet = workbook.add_worksheet("sheet1")
    for i in range(len(aus)):
        for j in range(len(aus[0])):
            worksheet.write(i+1,j,aus[i][j])
    workbook.close()

def time_cost_all(fn):
    num=[]
    def _wrapper(*args,**kwargs):
        start=time.time()
        A=fn(*args,**kwargs)
        dt=time.time()-start
        num.append(dt)
        print("%s 第 %s 次执行  耗时 %s  s 总耗时 %s   min"%(fn.__name__,len(num),round(dt,2),round(sum(num)/60,2)))
        return A
    return _wrapper

def time_cost1(filename='log.txt'):
    def time_cost(fn):
        def _wrapper(*args,**kwargs):
            doc=open(filename,'a')
            start=time.time()
            A=fn(*args,**kwargs)
            dt=time.time()-start
            if dt<60:
                print("%s cost %s second"%(fn.__name__,round(dt,2)))
                print("%s cost %s second"%(fn.__name__,round(dt,2)),file=doc)
            elif dt<3600:
                dm=int(dt/60)
                dt=dt-dm*60
                print("%s cost %s min %s second"%(fn.__name__,dm,round(dt,2)))
                print("%s cost %s min %s second"%(fn.__name__,dm,round(dt,2)),file=doc)
            else:
                dh=int(dt/3600)
                dm=int((dt-dh*3600)/60)
                dt=dt-dh*3600-dm*60
                print("%s cost %s hour %s min %s second"%(fn.__name__,dh,dm,round(dt,2)))
                print("%s cost %s hour %s min %s second"%(fn.__name__,dh,dm,round(dt,2)),file=doc)
            doc.close()
            return A
        return _wrapper
    
    return time_cost

def time_cost_all1(filename='log.txt'):
    
    def time_cost_all(fn):
        num=[]
        def _wrapper(*args,**kwargs):
            doc=open(filename,'a')
            start=time.time()
            A=fn(*args,**kwargs)
            dt=time.time()-start
            num.append(dt)
            print("%s 第 %s 次执行  耗时 %s  s 总耗时 %s   min"%(fn.__name__,len(num),round(dt,2),round(sum(num)/60,2)),file=doc)
            doc.close()
            return A
        return _wrapper
    
    return time_cost_all

def time_cost(fn):
    def _wrapper(*args,**kwargs):
        start=time.time()
        A=fn(*args,**kwargs)
        dt=time.time()-start
        if dt<60:
            print("%s cost %s second"%(fn.__name__,round(dt,2)))
        elif dt<3600:
            dm=int(dt/60)
            dt=dt-dm*60
            print("%s cost %s min %s second"%(fn.__name__,dm,round(dt,2)))
        else:
            dh=int(dt/3600)
            dm=int((dt-dh*3600)/60)
            dt=dt-dh*3600-dm*60
            print("%s cost %s hour %s min %s second"%(fn.__name__,dh,dm,round(dt,2)))
        return A
    return _wrapper