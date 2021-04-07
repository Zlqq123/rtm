var theme='essos';

var data1={
    index: [
        "0~20", "20~40", "40~60", "60~80", "80~100", "100~120","120~140", "140~160", "160~180", "180~200", "200~220", 
        "220~240", "240~260", "260~280", "280~300", "300~320", "320~340", "340~360", "360~380", "380~400", "400~420",
        "420~440", "440~460", "460~480"
    ],
    mile_convert:{
        March: [
            0.025, 0.064, 0.025, 0.115,0.102, 0.267, 0.534, 1.132, 2.43, 4.835, 9.453, 13.206, 16.463, 17.15, 13.944, 9.02, 4.873, 2.786, 1.501, 0.725, 0.534, 0.445, 0.216, 0.153],
        June: [
            0.06, 0.013, 0.026, 0.01, 0.034, 0.083, 0.232, 0.557, 1.423, 3.653, 8.651, 14.837, 18.943, 18.675, 14.247, 9.031, 4.666, 2.246, 1.108,0.523, 0.398, 0.233, 0.185, 0.166
        ],
        fleet: [
            0.079, 0.014, 0.038, 0.008, 0.027, 0.049, 0.12, 0.314, 0.959, 3.127, 8.313, 15.138, 19.629, 19.785, 15.125, 8.955, 4.442, 1.878, 0.858, 0.388, 0.301, 
            0.164, 0.15, 0.137
        ],
        taxi:[
            0.033, 0.0, 0.0, 0.0, 0.0, 0.017, 0.017, 0.067, 0.399, 1.779, 5.621, 13.255, 19.325, 20.855, 17.296, 11.758, 5.821, 2.079, 0.782, 0.333, 0.166, 0.233, 
            0.05, 0.116
        ],
        private: [
            0.036, 0.014, 0.023, 0.014, 0.054, 0.182, 0.49, 1.049, 2.37, 4.895, 9.672, 14.358, 17.641, 16.565, 12.319, 8.764, 4.85, 
            2.897, 1.589, 0.808, 0.572, 0.345, 0.259, 0.232
        ]
        },
    daily_mile_March:{
        lavida: [
            39.946, 21.271, 13.202, 8.005, 4.819, 3.513, 2.206, 1.57, 1.192, 0.95, 
            0.759, 0.585, 0.581, 0.339, 0.208, 0.263, 0.148, 0.14, 0.089, 0.072, 0.055, 0.025, 0.03, 0.03
            ], 
        tiguan: [
            39.693, 23.911, 13.943, 8.11, 4.623, 2.822, 1.829, 1.151, 0.868, 0.635, 0.435, 
            0.348, 0.302, 0.236, 0.184, 0.148, 0.142, 0.131, 0.118, 0.102, 0.074, 0.081, 0.066, 0.047
            ],
        passat: [
            37.103, 22.498, 13.571, 8.344, 5.19, 3.397, 2.222, 1.624, 1.211, 0.947, 0.743, 0.602, 0.496, 0.403, 0.297, 0.272, 0.224, 
            0.181, 0.159, 0.127, 0.113, 0.109, 0.096, 0.071
            ], 
        lavida_acc: [
            39.946, 61.217, 74.419, 82.424, 87.243, 90.756, 92.962, 94.532, 95.724, 96.674, 97.433, 98.019, 98.6, 98.939, 99.147, 99.41, 
            99.559, 99.699, 99.788, 99.86, 99.915, 99.941, 99.97, 100.0
            ], 
        tiguan_acc: [
            39.693, 63.604, 77.547, 85.656, 90.279, 93.102, 94.931, 96.082, 96.95, 97.585, 98.02, 98.369, 98.671, 98.906, 99.09, 99.239, 99.381, 
            99.512, 99.63, 99.732, 99.806, 99.886, 99.953, 100.0
            ], 
        passat_acc: [
            37.103, 59.601, 73.172, 81.516, 86.706, 90.103, 92.325, 93.949, 95.16, 96.108, 96.85, 97.453, 97.948, 98.351, 98.648, 
            98.92, 99.144, 99.325, 99.484, 99.611, 99.724, 99.833, 99.929, 100.0
            ]
    },
    daily_mile_June:{
        lavida: [
            23.286, 17.364, 12.485, 8.358, 5.452, 3.917, 2.834, 2.416, 2.325, 2.521, 2.697, 2.742, 2.727, 2.548, 2.209, 1.817, 
            1.341, 0.92, 0.643, 0.52, 0.368, 0.231, 0.185, 0.096
        ], 
        tiguan: [
            31.596, 23.959, 15.369, 9.629, 5.954, 3.731,2.383, 1.649, 1.184, 0.94, 0.681, 0.537, 0.467, 0.356, 0.286, 0.252, 0.214, 0.178, 
            0.166, 0.115, 0.11, 0.102, 0.074, 0.068
        ], 
        passat: [
            29.004, 21.897, 14.452, 9.481, 5.949, 4.014, 2.886, 2.206, 1.7, 1.443, 1.243, 1.039, 0.936, 0.766, 0.651, 0.517, 0.422, 0.327, 
            0.271, 0.225, 0.179, 0.148, 0.137, 0.106
        ], 
        lavida_acc: [
            23.286, 40.65, 53.135, 61.492, 66.944, 70.861, 73.695, 76.111, 78.435, 80.957, 83.654, 86.396, 89.123, 91.671, 93.88, 95.697, 
            97.038, 97.958, 98.601, 99.121, 99.489, 99.72, 99.904, 100.0
        ], 
        tiguan_acc: [
            31.596, 55.555, 70.924, 80.553, 86.506, 90.237, 92.62, 94.269, 95.454, 96.393, 97.074, 97.611, 98.078, 98.433, 98.72, 98.972, 
            99.186, 99.364, 99.53, 99.645, 99.756,99.858, 99.932, 100.0
        ], 
        passat_acc: [
            29.004, 50.902, 65.354, 74.835, 80.784, 84.798, 87.684, 89.889, 91.589, 93.032, 94.275, 95.314, 96.25, 97.016, 97.668, 98.185, 
            98.607, 98.934, 99.205, 99.43, 99.609, 99.757, 99.894, 100.0
        ],
        fleet: [
            15.0, 7.717, 5.766, 4.248, 3.522, 2.908, 2.95, 3.457, 3.945, 5.278, 6.035, 6.48, 6.615, 6.311, 5.558, 4.552, 3.334, 2.174, 1.517, 
            1.029, 0.722, 0.396, 0.307, 0.177
        ],
        taxi:[
            2.151, 1.14, 1.01, 1.14, 0.978, 1.89, 2.183, 2.639, 4.692, 6.126, 8.048, 8.602, 8.83, 9.58, 7.82, 6.973, 5.995, 4.366, 3.421, 3.91, 
            3.226, 2.411, 1.857, 1.01
        ],
        private: [
            31.515, 22.369, 15.45, 10.018, 6.104, 4.201, 2.658, 1.75, 1.349, 1.026, 0.813, 0.671, 0.573, 0.415, 0.355, 0.232, 0.147, 0.1, 0.066, 0.077, 
            0.053, 0.017, 0.028, 0.013
        ],
        fleet_acc:[
            15.0, 22.72, 28.48, 32.73, 36.25, 39.16, 42.11, 45.57, 49.51, 54.79, 60.83, 67.31, 73.92, 80.23, 85.79, 90.34, 93.68, 95.85, 97.37, 
            98.4, 99.12, 99.52, 99.82, 100.0
        ],
        taxi_acc:[2.15, 3.29, 4.3, 5.44, 6.42, 8.31, 10.49, 13.13, 17.82, 23.95, 32.0, 40.6, 49.43, 59.01, 66.83, 73.8, 79.8, 84.16, 87.59, 91.5, 94.72, 
            97.13, 98.99, 100.0],
        private_acc:[31.52, 53.88, 69.33, 79.35, 85.46, 89.66, 92.31, 94.06, 95.41, 96.44, 97.25, 97.92, 98.5, 98.91, 99.27, 99.5, 99.65, 99.75, 99.81, 
            99.89, 99.94, 99.96, 99.99, 100.0]
    },
    mile_perchanging_March:{
        lavida: [
            7.48, 7.93, 9.056, 8.48, 10.231, 10.794, 10.682, 9.406, 8.58, 6.504, 5.016, 3.177, 1.639, 0.738, 0.113, 0.038, 0.063, 0.013, 0.025, 
            0.013, 0.0, 0.0, 0.013, 0.013
        ], 
        tiguan: [
            20.696, 28.38, 19.564, 10.762, 6.029, 3.9, 2.579, 1.684, 1.418, 1.074, 0.745, 0.634, 0.431, 0.377, 0.271, 0.218, 0.247, 0.237, 
            0.179, 0.184, 0.068, 0.116, 0.082, 0.126
            ], 
        passat: [
            16.638, 25.409, 20.727, 11.826, 7.058, 4.501, 3.063, 2.248, 1.721, 1.281,
            1.002, 0.81, 0.64, 0.574, 0.449, 0.395, 0.339, 0.283, 0.259, 0.186, 0.189, 0.153, 0.13, 0.119
        ],
        lavida_acc: [
            7.48, 15.41, 24.465, 32.946, 43.177, 53.971, 64.653, 74.059, 82.639, 89.143, 94.159, 97.336, 98.974, 99.712, 99.825, 99.862, 
            99.925, 99.937, 99.962, 99.975, 99.975, 99.975, 99.987, 100.0], 
        tiguan_acc: [
            20.696, 49.076, 68.639, 79.401, 85.43, 89.33, 91.909, 93.593, 95.011, 96.085, 96.831, 97.464, 97.895, 98.273, 
            98.544, 98.761, 99.008, 99.245, 99.424, 99.608, 99.676, 99.792, 99.874, 100.0], 
        passat_acc: [
            16.638, 42.048, 62.775, 74.6, 81.658, 86.159, 89.221, 91.469, 93.191, 94.471, 95.474, 96.284, 96.923, 97.497, 97.946, 
            98.341, 98.68, 98.963, 99.222, 99.408, 99.597, 99.75, 99.881, 100.0]
        
    },
    mile_perchanging_June:{
        lavida: [
            5.844, 6.51, 7.377, 8.527, 10.41, 11.103, 10.949, 10.747, 9.594, 7.79, 5.389, 3.133, 1.556, 0.572, 0.212, 0.062, 0.052, 0.04, 
            0.033, 0.03, 0.027, 0.016, 0.01, 0.019
        ], 
        tiguan: [
            18.64, 27.873, 20.227, 10.86, 6.359, 4.034, 2.705, 1.872, 1.441, 1.106, 0.82, 0.686, 0.594, 0.458, 0.373, 0.355, 0.317, 0.252, 0.208, 0.219, 
            0.176, 0.174, 0.133, 0.118
        ], 
        passat: [
            15.298, 23.364, 19.828, 11.64, 7.02, 4.733, 3.396, 2.632, 2.009, 1.609,1.332, 1.192, 1.008, 0.909, 0.763, 0.673, 0.492, 0.445, 0.39, 0.343, 
            0.265, 0.238, 0.219, 0.203
        ], 
        lavida_acc: [
            5.844, 12.354, 19.73, 28.258, 38.668, 49.77, 60.719, 71.466, 81.06, 88.85, 94.238, 97.371, 98.927, 99.499, 99.711, 99.773, 99.824, 
            99.865, 99.898, 99.928, 99.955, 99.971, 99.981, 100.0
        ], 
        tiguan_acc: [
            18.64, 46.512, 66.739, 77.599, 83.958, 87.992, 90.697, 92.569, 94.009, 95.116, 95.936, 96.622, 97.216, 97.674, 98.047, 98.402, 98.719, 
            98.971, 99.18, 99.399, 99.575, 99.749, 99.882, 100.0
        ], 
        passat_acc: [
            15.298, 38.662, 58.49, 70.13, 77.15, 81.883, 85.279, 87.911, 89.92, 91.528, 92.861, 94.053, 95.061, 95.97, 96.733, 97.406, 97.897, 98.343, 
            98.733, 99.075, 99.34, 99.578, 99.797, 100.0
        ],
        fleet: [
            5.186, 6.093, 6.898, 8.509, 10.589, 11.493, 11.545, 11.301, 9.906, 7.873, 5.162, 3.082, 1.519, 0.504, 0.165, 0.054, 0.024, 0.019, 0.022, 0.011, 
            0.014, 0.011, 0.003, 0.019
        ],
        taxi:[
            1.541, 2.768, 4.74, 7.309, 10.209, 12.214, 12.214, 13.01, 11.717, 10.54, 7.375, 4.176, 1.525, 0.398, 0.133, 0.033, 
            0.033, 0.033, 0.017, 0.0, 0.0, 0.0, 0.017, 0.0
        ],
        private: [
            7.671, 7.921, 8.505, 8.715, 9.959, 10.521, 9.924, 9.406, 8.822, 7.132, 5.308, 2.988, 1.606, 0.714, 0.317, 0.085, 0.094, 0.071, 0.049, 0.071, 
            0.054, 0.031, 0.018, 0.018
        ],
        fleet_acc:[
            5.19, 11.28, 18.18, 26.69, 37.27, 48.77, 60.31, 71.61, 81.52, 89.39, 94.55, 97.64, 99.16, 99.66, 99.82, 99.88, 99.9, 99.92, 99.94, 
            99.95, 99.97, 99.98, 99.98, 100.0
        ],
        taxi_acc:[
            1.54, 4.31, 9.05, 16.36, 26.57, 38.78, 50.99, 64.0, 75.72, 86.26, 93.64, 97.81, 99.34, 99.73, 99.87, 99.9, 99.93, 99.97, 99.98, 99.98, 
            99.98, 99.98, 100.0, 100.0
        ],
        private_acc:[
            7.67, 15.59, 24.1, 32.81, 42.77, 53.29, 63.22, 72.62, 81.45, 88.58, 93.89, 96.87, 98.48, 99.19, 99.51, 99.59, 99.69, 99.76, 99.81, 99.88, 
            99.93, 99.96, 99.98, 100.0
        ]
    }
};



var myChart1 = echarts.init(document.getElementById('mile_f1'),theme);
var option1={
        title : {text: 'Lavida 每日行驶里程',left: '30%',textAlign: 'center'},
        grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        legend: { orient: 'vertical',left:"85%",top: '12%',
                data: ['三月', '六月','三月（累积）', '六月（累积）']},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: { type: 'category',name:"里程[km]",nameLocation: 'middle',nameGap: 25,
                axisTick:{show:true,alignWithLabel:true,interval:0,rotate:40,},
                data: data1.index},
        yAxis: [{type: 'value',min: 0,name:"占比",
            interval: 5,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
            {type: 'value',min: 0,name:"累计百分比",
            interval: 10,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}}
        ],
        series: [
            {name:"三月",type: 'bar',data:data1.daily_mile_March.lavida},
            {name:"六月",type: 'bar',data:data1.daily_mile_June.lavida},
            {name:"三月（累积）",type: 'line',yAxisIndex: 1,data:data1.daily_mile_March.lavida_acc},
            {name:"六月（累积）",type: 'line',yAxisIndex: 1,data:data1.daily_mile_June.lavida_acc},
            ]
            };
myChart1.setOption(option1);

var myChart2 = echarts.init(document.getElementById('mile_f2'),theme);
var option2={
        title : {text: 'PHEV 每日行驶里程',left: '30%'},
        grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        legend: { orient: 'vertical',left:"85%",top: '12%',
                data: ['Tiguan', 'Passat','Tiguan（累积）', 'Passat（累积）']},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: { type: 'category',name:"里程[km]",nameLocation: 'middle',nameGap: 25,
                axisTick:{show:true},data: data1.index},
        yAxis: [{type: 'value',min: 0,name:"占比",
            interval: 5,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
            {type: 'value',min: 0,name:"累计百分比",
            interval: 10,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
        ],
        series: [
            {name:"Tiguan",type: 'bar',data:data1.daily_mile_June.tiguan},
            {name:"Passat",type: 'bar',data:data1.daily_mile_June.passat},
            {name:"Tiguan（累积）",type: 'line',yAxisIndex: 1,data:data1.daily_mile_June.tiguan_acc},
            {name:"Passat（累积）",type: 'line',yAxisIndex: 1,data:data1.daily_mile_June.passat_acc}
            ]
            };
myChart2.setOption(option2);



var myChart3 = echarts.init(document.getElementById('mile_f3'),theme);
var option3={
        title : {text: 'Lavida 估算全电里程',left: '30%'},
        grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
        tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        legend: { orient: 'vertical',left:"85%",top: '12%',
                data: ['三月', '六月']},
        toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'},
                                        magicType: {type: ['bar', 'line'],title:{line:'折线图',bar:'柱状图'}},
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
        xAxis: { type: 'category',name:"里程[km]",nameLocation: 'middle',nameGap: 25,
                axisTick:{show:true},data: data1.index},
        yAxis: {type: 'value',min: 0,name:"占比",
            interval: 5,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
        series: [{name:"三月",type: 'line',data:data1.mile_convert.March},
            {name:"六月",type: 'line',data:data1.mile_convert.June}]
            };
myChart3.setOption(option3);

var data2={
        index: ["9.0~9.5", "9.5~10.0", "10.0~10.5", "10.5~11.0", "11.0~11.5", "11.5~12.0", "12.0~12.5", "12.5~13.0", "13.0~13.5", "13.5~14.0", "14.0~14.5", "14.5~15.0", 
        "15.0~15.5", "15.5~16.0", "16.0~16.5", "16.5~17.0", "17.0~17.5", "17.5~18.0",  "18.0~18.5", "18.5~19.0", "19.0~19.5", "19.5~20.0", "20.0~20.5"],
        March: [0.634, 1.308, 1.599, 2.72, 3.819, 5.56, 6.911, 8.51, 8.841, 8.93, 8.761, 7.57, 6.13, 5.89, 4.916, 3.8, 
        3.34, 2.867, 2.43, 1.889, 1.4140, 1.21, 0.845],
        June: [0.532, 0.7170, 1.339, 2.168, 3.42, 5.079, 6.865, 7.952, 8.94, 9.253, 8.80, 8.214, 6.9, 6.022, 5.014, 3.98, 
        3.12, 2.3857, 1.685, 1.389, 1.047, 0.725, 0.56]
};
var myChart4 = echarts.init(document.getElementById('mile_f4'),theme);
var option4={
            title:{ text: 'Lavida估算能耗',left: '30%'},
            grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
            tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
            toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        magicType: {type: ['bar', 'line'],title:{line:'折线图',bar:'柱状图'}},
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
            legend: {orient: 'vertical',left:"85%",top: '12%',data: ['三月', '六月']},
            xAxis: { type: 'category',name:"电耗[kWh/100km]",nameLocation: 'middle',nameGap: 25,
                    axisTick:{show:true},data: data2.index},
            yAxis: {type: 'value',min: 0,name:"占比",interval: 2,axisLabel: {formatter: '{value} %'},
                    axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
                    
            series: [{name:"三月",type: 'line',data:data2.March},
                    {name:"六月",type: 'line',data:data2.June}
                    ]
            };
myChart4.setOption(option4);

var myChart5 = echarts.init(document.getElementById('mile_f5'),theme);
var option5={
            title:{ text: '不同车型每次充电之间的里程',left: '30%'},
            grid:{x:"5%",y:'15%',x2:"22%",y2:'15%'},
            tooltip: {trigger: 'axis',axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
            toolbox: { show: true,feature: {dataView: {show: true, readOnly: false, title:'查看数据'}, 
                                        saveAsImage: {show:true, title:'保存为图片图'},
                                        restore: {show: true, title:'重置'}
                                    }},
            legend: {orient: 'vertical',left:"85%",top: '12%',
                    data: ['Lavida', 'Tiguan','Passat','Lavida(累积)','Tiguan(累积)','Passat(累积)']},
            xAxis: { type: 'category',name:"里程[km]",nameLocation: 'middle',nameGap: 25,
                    axisTick:{show:true},data: data1.index},
            yAxis: [{type: 'value',min: 0,name:"占比",interval: 2,axisLabel: {formatter: '{value} %'},
                    axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
                    {type: 'value',min: 0,name:"累计百分比",interval: 10,axisLabel: {formatter: '{value} %'},
                    axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}}],
            series: [{name:"Lavida",type: 'bar',data:data1.mile_perchanging_June.lavida},
                    {name:"Tiguan",type: 'bar',data:data1.mile_perchanging_June.tiguan},
                    {name:"Passat",type: 'bar',data:data1.mile_perchanging_June.passat},
                    {name:"Lavida(累积)",type: 'line',yAxisIndex: 1,data:data1.mile_perchanging_June.lavida_acc},
                    {name:"Tiguan(累积)",type: 'line',yAxisIndex: 1,data:data1.mile_perchanging_June.tiguan_acc},
                    {name:"Passat(累积)",type: 'line',yAxisIndex: 1,data:data1.mile_perchanging_June.passat_acc}
                    ]
            };
myChart5.setOption(option5);
