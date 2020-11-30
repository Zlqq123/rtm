var theme='essos';

var data={
    index: [
        "0~10%", "10~20%", "20~30%", "30~40%", "40~50%", "50~60%", "60~70%", "70~80%", 
        "80~90%", "90~100%", '100%'], 
    col: ["Lavida BEV", "Tiguan L PHEV", "Passat PHEV"], 
    start_soc:{
        lavida: [4.664, 9.664, 15.538, 16.864, 15.389, 13.477, 10.923, 7.38, 4.235, 1.8, 0.066],
        tiguan: [46.337, 11.498, 9.56, 8.309, 6.419, 5.849, 4.967, 3.55, 2.367, 0.998, 0.147],
        passat: [46.865, 13.276, 9.738, 8.018, 6.192, 5.284, 4.495, 3.217, 2.021, 0.835, 0.061],
    },
    end_soc:{
        lavida:[0.13, 0.386, 1.029, 1.95, 2.581, 3.714, 4.986, 6.447, 8.884, 22.717, 47.176],
        tiguan:[1.207, 1.287, 1.617, 2.379, 2.199, 2.352, 2.985, 3.195, 3.622, 27.714, 51.444],
        passat:[0.717, 1.143, 1.528, 2.058, 2.082, 2.418, 2.764, 3.064, 3.376, 29.57, 51.279]
    }
};


var myChart1 = echarts.init(document.getElementById("charge_soc_f1"),theme);
var option1={
    title : {text: '用户开始充电SOC分布',left: '20%'},
    grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
    tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
    legend: { orient: 'vertical',left:"85%",top: '12%',
            data: data.col},
    toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                    saveAsImage: {show:true, title:'保存为图片图'},
                                    restore: {show: true, title:'重置'}
                                }},
    xAxis: { type: 'category',name:"SOC[%]",nameLocation: 'middle',nameGap: 25,
            axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
            data: data.index
        },
    yAxis: {type: 'value',min: 0,name:"占比",
        interval: 5,axisLabel: {formatter: '{value} %'},
        axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
        
    series: [
        {name:"Lavida BEV",type: 'bar',data:data.start_soc.lavida},
        {name:"Tiguan L PHEV",type: 'bar',data:data.start_soc.tiguan},
        {name:"Passat PHEV",type: 'bar',data:data.start_soc.passat}
        ]
        };
myChart1.setOption(option1);

var myChart2 = echarts.init(document.getElementById("charge_soc_f2"),theme);
var option2 = {
    title : {text: '用户结束充电SOC分布',left: '20%'},
    grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
    tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
    legend: { orient: 'vertical',left:"85%",top: '12%',
            data: data.col},
    toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                    saveAsImage: {show:true, title:'保存为图片图'},
                                    restore: {show: true, title:'重置'}
                                }},
    xAxis: { type: 'category',name:"SOC[%]",nameLocation: 'middle',nameGap: 25,
            axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
            data: data.index
        },
    yAxis: {type: 'value',min: 0,name:"占比",
        interval: 5,axisLabel: {formatter: '{value} %'},
        axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
        
    series: [
        {name:"Lavida BEV",type: 'bar',data:data.end_soc.lavida},
        {name:"Tiguan L PHEV",type: 'bar',data:data.end_soc.tiguan},
        {name:"Passat PHEV",type: 'bar',data:data.end_soc.passat}
        ]
        };
myChart2.setOption(option2);