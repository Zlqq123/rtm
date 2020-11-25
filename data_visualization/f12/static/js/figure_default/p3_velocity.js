var theme='essos';

var data1={
    index: [
        "0~10", "10~20", "20~30", "30~40", "40~50", "50~60", "60~70", "70~80", "80~90", 
        "90~100", "100~110", "110~120", ">120"], 
    March:{
        lavida: [
            15.07, 13.427, 14.158, 14.374, 13.249, 10.709, 7.424, 5.041, 2.843, 1.89, 
            1.082, 0.594, 0.141], 
        tiguan: [
            15.377, 12.874, 12.982, 12.708, 11.758, 9.61, 7.156, 5.372, 3.615, 3.302, 
            2.592, 1.98, 0.674], 
        passat: [15.341, 12.586, 12.952, 12.535, 11.506, 9.449, 7.027, 5.403, 
            3.643, 3.414, 2.833, 2.355, 0.957], 
        lavida_acc: [
            15.07, 28.496, 42.654, 57.028, 70.277, 80.986, 88.409, 
            93.45, 96.293, 98.184, 99.265, 99.859, 100.0], 
        tiguan_acc: [
            15.377, 28.251, 41.233, 53.941, 65.698, 75.308, 82.465, 87.837, 91.452, 94.755, 
            97.346, 99.326, 100.0], 
        passat_acc: [
            15.341, 27.927, 40.878, 53.413, 64.919, 74.368, 81.396, 86.799, 90.441, 93.855, 
            96.688, 99.043, 100.0]
        },
    June:{
        lavida: [
            17.531, 16.026, 16.203, 15.502, 13.124, 9.541, 5.945, 3.39, 1.416, 
            0.727, 0.532, 0.048, 0.016], 
        tiguan: [
            17.592, 14.729, 13.832, 12.847, 11.359, 9.022, 6.422, 4.419, 2.846, 
            2.64, 2.377, 1.281, 0.634], 
        passat: [
            17.596, 14.491, 13.954, 12.895, 11.388, 9.038, 6.353, 
            4.447, 2.825, 2.603, 2.055, 1.476, 0.879], 
        lavida_acc: [
            17.531, 33.557, 49.76, 65.262, 78.387, 87.927, 93.872, 97.262, 98.678,
            99.405, 99.937, 99.984, 100.0], 
        tiguan_acc: [
            17.592, 32.321, 46.152, 58.999, 70.358, 79.381, 85.802, 90.222, 93.068, 
            95.708, 98.084, 99.366, 100.0], 
        passat_acc: [
            17.596, 32.087, 46.041, 58.937, 70.325, 79.363, 85.716, 90.162, 92.987, 
            95.59, 97.645, 99.121, 100.0]
        },
    CLTC: [
        30.21, 14.6, 12.66, 11.49, 9.66, 9.38, 4.28, 2.94, 1.39, 1.39, 0.94, 1.05, 0.0], 
    NEDC: [
        31.5, 8.64, 6.44, 17.61, 14.48, 1.61, 10.16, 1.19, 1.35, 3.9, 1.19, 1.95, 0.0], 
    WLTP: [
        16.55, 11.6, 12.16, 8.27, 10.16, 9.44, 7.38, 5.05, 4.22, 5.05, 2.55, 2.83, 4.72], 
    CLTC_acc: [
        30.21, 44.81, 57.47, 68.96, 78.62, 88.0, 92.28, 95.22, 96.61, 98.0, 98.94, 99.99, 99.99], 
    NEDC_acc: [
        31.5, 40.14, 46.58, 64.19, 78.67, 80.28, 90.44, 91.63, 92.98, 96.88, 98.07, 100.02, 100.02], 
    WLTP_acc: [
        16.55, 28.15, 40.31, 48.58, 58.74, 68.18, 75.56, 80.61, 84.83, 89.88, 92.43, 95.26, 99.98],
    drive_mode:{
        tiguan:[{name: "EV", value: 54.8},  {name: "PHEV", value: 4.1},{name: "FV", value: 41.1}],
        passat:[{name: "EV", value: 60.2},  {name: "PHEV", value: 3.4},{name: "FV", value: 36.3}]
        },
    drive_mode_v:{
        tiguan:{
                EV: [85.861, 77.242, 65.81, 61.941, 56.559, 50.797, 41.492, 29.463, 
                    23.473, 17.763, 13.206, 8.86, 7.067], 
                PHEV: [0.601, 2.694, 3.643, 2.909, 3.959, 5.609, 7.884, 8.84, 7.86, 
                    6.81, 5.758, 3.916, 4.758], 
                FV: [13.537, 20.064, 30.547, 35.149, 39.481, 43.594, 50.624, 61.697, 
                    68.667, 75.426, 81.035, 87.223, 88.175]
            },
        passat:{
                EV: [88.078, 81.421, 72.872, 68.399, 62.131, 55.369, 46.428, 
                    33.761, 26.077, 18.604, 13.283, 8.764, 6.458], 
                PHEV: [0.499, 2.226, 2.502, 2.574, 3.677, 5.373, 7.463, 7.788, 
                    6.285, 4.665, 3.769, 2.18, 2.844], 
                FV: [11.423, 16.353, 24.627, 29.026, 34.192, 39.258, 46.109, 
                    58.451, 67.638, 76.731, 82.949, 89.057, 90.698]
                }
        }
    };

var myChart1 = echarts.init(document.getElementById('velocity_f1'),theme);
var option1={
        title : {text: 'Lavida BEV 用户工况 & NEDC & CLTC 车速分布',left: '20%'},
        grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        legend: { orient: 'vertical',left:"85%",top: '12%',
                data: ['用户工况', 'NEDC','CLTC','用户工况(累积)', 'NEDC(累积)','CLTC(累积)']},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: { type: 'category',name:"车速[km/h]",nameLocation: 'middle',nameGap: 25,
                axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
                data: data1.index
            },
        yAxis: [{type: 'value',min: 0,name:"占比",
            interval: 5,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
            {type: 'value',min: 0,name:"累积百分比",
            interval: 10,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}}
        ],
        series: [
            {name:"用户工况",type: 'bar',data:data1.June.lavida},
            {name:"NEDC",type: 'bar',data:data1.NEDC},
            {name:"CLTC",type: 'bar',data:data1.CLTC},
            {name:"用户工况(累积)",type: 'line',yAxisIndex: 1,data:data1.June.lavida_acc},
            {name:"NEDC(累积)",type: 'line',yAxisIndex: 1,data:data1.NEDC_acc},
            {name:"CLTC(累积)",type: 'line',yAxisIndex: 1,data:data1.CLTC_acc},
            ]
            };
myChart1.setOption(option1);

var myChart2 = echarts.init(document.getElementById('velocity_f2'),theme);
var option2={
        title : {text: 'PHEV 用户工况 & NEDC & WLTP 车速分布',left: '20%'},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
        legend: { orient: 'vertical',left:"85%",top: '12%',
                data: ['Tiguan 用户工况', 'Passat 用户工况', 'NEDC','WLTP',
                    'Tiguan 用户工况(累积)', 'Passat 用户工况(累积)', 'NEDC(累积)','WLTP(累积)']},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: { type: 'category',name:"车速[km/h]",nameLocation: 'middle',nameGap: 25,
                axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
                data: data1.index
                },
        yAxis: [{type: 'value',min: 0,name:"占比",
            interval: 5,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
            {type: 'value',min: 0,name:"累积百分比",
            interval: 10,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}}
        ],
        series: [
            {name:"Tiguan 用户工况",type: 'bar',data:data1.June.tiguan},
            {name:"Passat 用户工况",type: 'bar',data:data1.June.passat},
            {name:"NEDC",type: 'bar',data:data1.NEDC},
            {name:"WLTP",type: 'bar',data:data1.WLTP},
            {name:"Tiguan 用户工况(累积)",type: 'line',yAxisIndex: 1,data:data1.June.tiguan_acc},
            {name:"Passat 用户工况(累积)",type: 'line',yAxisIndex: 1,data:data1.June.passat_acc},
            {name:"NEDC(累积)",type: 'line',yAxisIndex: 1,data:data1.NEDC_acc},
            {name:"WLTP(累积)",type: 'line',yAxisIndex: 1,data:data1.WLTP_acc},
            ]
            };
myChart2.setOption(option2);

var myChart3 = echarts.init(document.getElementById('velocity_f3'),theme);
var option3 ={
        legend: { 
                type: 'scroll',orient: 'vertical',right: 10,top: 20,
                data: ['EV', 'PHEV','FV']
                },
        tooltip: {trigger: 'item'},
        series: [{name: 'project',
                type: 'pie',
                radius: '55%',
                center: ['40%', '50%'],
                data:data1.drive_mode.passat }]
        };
myChart3.setOption(option3);

var myChart4 = echarts.init(document.getElementById('velocity_f4'),theme);
var option4 = {
        title : {text: 'PHEV 用户工况 & NEDC & WLTP 车速分布',left: '20%'},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        grid:{x:"5%",y:'20%',x2:"22%",y2:'15%'},
        legend: { orient: 'vertical',left:"85%",top: '12%',
                data: ['EV', 'PHEV','FV']},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: { type: 'category',name:"车速[km/h]",nameLocation: 'middle',nameGap: 25,
                axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
                data: data1.index
                },
        yAxis: {type: 'value',min: 0,name:"占比",max:100,
            interval: 10,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}
            },
        series: [
            {name:"EV",type: 'bar',stack: 'mode',data:data1.drive_mode_v.passat.EV},
            {name:"PHEV",type: 'bar',stack: 'mode',data:data1.drive_mode_v.passat.PHEV},
            {name:"FV",type: 'bar',stack: 'mode',data:data1.drive_mode_v.passat.FV}
            ]
        };
myChart4.setOption(option4);