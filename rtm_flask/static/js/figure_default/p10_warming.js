var theme='essos';

var data1={
    index: [
        "温度差异报警", "电池高温报警", "车载储能装置类型过压报警", "车载储能装置类型欠压报警", 
        "SOC低报警", "单体电池过压报警", "单体电池欠压报警", "SOC过高报警", "SOC跳变报警", 
        "可充电储能系统不匹配报警", "电池单体一致性差报警", "绝缘报警", "dc-dc温度报警", 
        "制动系统报警", "DC-DC状态报警", "驱动电机控制器温度报警", "高压互锁状态报警", 
        "驱动电机温度报警", "车载储能装置类型过充", "total"], 
    col: ["Lavida BEV", "Tiguan L PHEV", "Passat PHEV"], 
    warming_num:{
        lavida: [0, 1706, 0, 0, 0, 0, 0, 0, 73, 0, 0, 17085, 0, 716, 26, 8, 734, 0, 0, 19878], 
        tiguan: [
            3024, 55, 0, 0, 54, 0, 0, 0, 2052, 0, 8107, 7649, 13, 3647, 30, 84, 
            8291, 0, 0, 32766],
        Passat: [
            0, 1156, 0, 0, 610, 0, 0, 0, 2442, 0, 3759, 3622, 755, 6734, 
            382, 1526, 3718, 0, 0, 22219], 
    },
    vehicle_involve:{
        lavida: [0, 9, 0, 0, 0, 0, 0, 0, 15, 0, 0, 190, 0, 13, 1, 1, 8, 0, 0, 228],
        tiguan: [1, 1, 0, 0, 1, 0, 0, 0, 33, 0, 1, 8, 2, 713, 2, 1, 285, 0, 0, 1005],
        passat: [0, 8, 0, 0, 4, 0, 0, 0, 51, 0, 1, 2, 1, 203, 9, 2, 57, 0, 0, 297]
    }
};
    
var myChart1 = echarts.init(document.getElementById('warm_f1'),theme);
var option1={
        title : {text: 'RTM报警发生次数统计（2020年6月）',left: '20%'},
        grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        legend: { orient: 'vertical',left:"85%",top: '12%',
                data: ["Lavida BEV", "Tiguan L PHEV", "Passat PHEV"]},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: { type: 'category',
                axisTick:{show:true ,interval:0, rotate:40},
                data: data.index
            },
        yAxis: {
            type: 'value',min: 0,name:"发生次数",
            interval: 200,
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}
        },
            
        series: [
            {name:"Lavida BEV",type: 'bar',data:data.warming_num.lavida},
            {name:"Tiguan L PHEV",type: 'bar',data:data.warming_num.tiguan},
            {name:"Passat PHEV",type: 'bar',data:data.warming_num.passat},
            ]
            };
myChart1.setOption(option1);
