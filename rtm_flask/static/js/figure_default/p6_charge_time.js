var theme='essos';

var data={
    charge_start_time:{
        index: ["0~1", "1~2", "2~3", "3~4", "4~5", "5~6", "6~7", "7~8", "8~9", 
            "9~10", "10~11", "11~12", "12~13", "13~14", "14~15", "15~16", "16~17", 
            "17~18", "18~19", "19~20", "20~21", "21~22", "22~23", "23~24"],
        col: ["Lavida BEV", "Tiguan L PHEV", "Passat PHEV"],
        lavida_june: [
            4.376, 2.447, 1.524, 1.161, 1.066, 1.418, 2.024, 2.439, 3.729, 4.242, 4.588, 6.204, 6.066, 
            5.151, 5.313, 6.085, 6.329, 4.872, 4.47, 4.893, 5.056, 4.84, 5.265, 6.443], 
        tiguan_june: [
            2.332, 0.943, 0.662, 0.611, 0.411, 0.435, 0.938, 4.178, 6.607, 4.819, 3.972, 4.746, 4.917, 
            3.774, 3.546, 3.696, 4.543, 7.286, 8.409, 7.621, 7.401, 7.685, 6.662, 3.804], 
        passat_june: [
            2.806, 1.317, 0.747, 0.519, 0.367, 0.461, 1.086, 4.089, 6.441, 4.522, 3.974, 4.772, 
            4.74, 3.592, 3.627, 3.514, 4.395, 6.281, 7.95, 7.19, 7.336, 7.978, 7.555, 4.74]
    },
    charge_time:{
        index: [
            "0~0.5", "0.5~1", "1~2", "2~3", "3~4", "4~5", "5~6", "6~7", "7~8", "8~9", 
            "9~10", "10~11", "11~12", "12~13", "13~14", "14~15", "15~25"], 
        col: ["模式二", "模式三(3.6kW)","模式三(7.2kW)","直流充电"], 
        lavida_original:{
            mode2: [9.548, 18.786, 14.794, 5.853, 5.017, 4.167, 3.601, 4.464, 5.448, 5.381, 5.799, 4.72, 3.196, 
                .832, 1.794, 1.227, 3.372], 
            mode3_3: [15.212, 26.274, 20.006, 8.1, 5.781, 5.223, 4.651, 4.379, 3.735, 3.177, 2.147, 0.758,
                0.215, 0.143, 0.014, 0.029, 0.157], 
            mode3_7: [11.891, 20.618, 22.474, 14.985, 14.328, 11.846, 2.441, 0.307, 0.202, 0.157, 0.125, 
                0.093, 0.073, 0.069, 0.065, 0.052, 0.274], 
            DC: [29.942, 46.192, 22.056, 1.195, 0.302, 0.098, 0.039, 0.051, 0.031, 0.024, 0.02, 0.027, 
                0.008, 0.008, 0.0, 0.0, 0.008] 
        },
        lavida_convert:{
            mode2:[0.056, 2.147, 9.467, 6.146, 1.166, 0.389, 0.629, 0.352, 0.093, 0.074, 0.093, 0.074, 
            0.093, 0.111, 0.148, 0.093, 48.871],
            mode3_3:[0.0, 2.508, 4.464, 5.858, 0.971, 0.522, 0.478, 0.261, 0.13, 0.261,
             0.594, 8.105, 15.876, 13.354, 6.496, 3.944, 6.177],
            mode3_7:[0.008, 1.663, 4.347, 3.846, 0.815, 0.694, 38.238, 
            23.852, 2.856, 1.156, 0.617, 0.398, 0.345, 0.187, 0.256, 0.126, 0.596],
            DC:[0.008, 5.753, 79.048, 11.546, 2.191, 0.686, 0.274, 0.141, 0.09, 0.063, 0.031, 0.039, 0.027,
             0.027, 0.016, 0.0, 0.059]
        },
        tiguan_original:{
            mode2:[3.622, 4.736, 12.186, 13.1, 14.866, 15.964, 18.967, 10.442, 1.326, 0.802, 0.986, 
            1.265, 0.908, 0.273, 0.145, 0.128, 0.284],
            mode3_3:[3.931, 7.83, 22.368, 32.03, 31.03, 0.634, 0.332, 0.31, 0.272, 0.238, 
            0.19, 0.223, 0.187, 0.143, 0.069, 0.064, 0.149],
        },
        tiguan_convert:{
            mode2:[0.011, 0.028, 0.034, 0.146, 3.142, 6.777, 27.747, 42.377,
            8.973, 2.168, 1.031, 1.91, 2.761, 1.115, 0.459, 0.291, 1.031],
            mode3_3:[0.008, 0.002, 0.112, 6.556, 83.191, 6.155, 1.336, 0.547, 0.354, 0.295, 0.234, 0.234, 
            0.214, 0.155, 0.126, 0.114, 0.368]
        },
        passat_original:{
            mode2:[2.476, 3.96, 10.191, 11.5, 13.791, 16.93, 22.735, 13.278, 1.245, 0.85, 0.896, 
            1.023, 0.545, 0.161, 0.141, 0.061, 0.216],
            mode3_3:[3.295, 7.256, 20.937, 33.422, 32.693, 0.564, 0.276, 0.276, 
            0.277, 0.276, 0.206, 0.142, 0.105, 0.066, 0.066, 0.034, 0.108],
        },
        passat_convert:{
            mode2:[0.006, 0.012, 0.023, 0.072, 1.692, 5.413, 27.659, 46.582, 9.011, 1.941, 0.848, 1.444, 
            2.459, 1.212, 0.527, 0.208, 0.891],
            mode3_3:[0.002, 0.002, 0.059, 5.902, 84.493, 5.982, 1.233, 0.541, 0.366, 0.306, 0.257, 0.176, 0.129, 
            0.117, 0.093, 0.065, 0.277]
        }
    }
    
};


var myChart1 = echarts.init(document.getElementById("charge_time_f1"),theme);
var option1={
    title : {text: '用户开始充电时间分布',left: '20%'},
    grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
    tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
    legend: { orient: 'vertical',left:"85%",top: '12%',
            data: data.charge_start_time.col},
    toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                    saveAsImage: {show:true, title:'保存为图片图'},
                                    restore: {show: true, title:'重置'}
                                }},
    xAxis: { type: 'category',name:"时刻[时]",nameLocation: 'middle',nameGap: 25,
            axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
            data: data.charge_start_time.index
        },
    yAxis: {type: 'value',min: 0,name:"占比",
        interval: 2 ,axisLabel: {formatter: '{value} %'},
        axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
        
    series: [
        {name:"Lavida BEV",type: 'line',data:data.charge_start_time.lavida_june},
        {name:"Tiguan L PHEV",type: 'line',data:data.charge_start_time.tiguan_june},
        {name:"Passat PHEV",type: 'line',data:data.charge_start_time.passat_june}
        ]
        };
myChart1.setOption(option1);


var myChart2 = echarts.init(document.getElementById("charge_time_f2"),theme);
var option2={
    title : {text: 'Lavida折算满充时间分布',left: '20%'},
    grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
    tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
    legend: { orient: 'vertical',left:"85%",top: '12%',
            data: data.charge_time.col},
    toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                    saveAsImage: {show:true, title:'保存为图片图'},
                                    restore: {show: true, title:'重置'}
                                }},
    xAxis: { type: 'category',name:"时间",nameLocation: 'middle',nameGap: 25,
            axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
            axisLabel: {formatter: '{value} h'},
            data: data.charge_time.index
        },
    yAxis: {type: 'value',min: 0,name:"占比",
        interval: 5 ,axisLabel: {formatter: '{value} %'},
        axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
        
    series: [
        {name:"模式二",type: 'line',data:data.charge_time.lavida_convert.mode2},
        {name:"模式三(3.6kW)",type: 'line',data:data.charge_time.lavida_convert.mode3_3},
        {name:"模式三(7.2kW)",type: 'line',data:data.charge_time.lavida_convert.mode3_7},
        {name:"直流充电",type: 'line',data:data.charge_time.lavida_convert.DC}
        ]
        };
myChart2.setOption(option2);