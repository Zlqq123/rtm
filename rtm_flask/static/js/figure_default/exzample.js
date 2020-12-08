var theme='essos';


var theme='walden';



var myChart4 = echarts.init(document.getElementById('mile_f1'),theme);

var option4 = {
        grid:{top: "50%"},
        title:{ text: 'Lavida不同地理位置车辆每日行驶里程分布',x:'center', y: 'top',},
        tooltip: {trigger: 'axis',
                axisPointer: {type: 'cross',crossStyle: {color: '#999'}}},
        toolbox: {feature: {dataView: {show: true, readOnly: false},
                            magicType: {show: true, type: ['line', 'bar']},
                            restore: {show: true},
                            saveAsImage: {show: true}}},
        legend: {data: ['华北','华北累计百分比'],x:'center', y: 'top'},
        xAxis: [{type: 'category',
                data: ['0~20', '20~40', '40~60', '60~80', '80~100', '100~120', '120~140', '140~160', '160~180', '180~200', '200~220', 
                '220~240','240~260','260~280','280~300','300~320','320~340','340~360','360~380','380~400','400~420','420~440'],
                axisPointer: { type: 'shadow'}
                }],
        yAxis: [{type: 'value',name: '占比',min: 0,max: 40,
                interval: 5,axisLabel: {formatter: '{value} %'}},
            {type: 'value',name: '累计百分比', min: 0,max: 120,
                interval: 10,axisLabel: { formatter: '{value} %'}}
                ],
        series: [{name: '华北',type: 'bar',
                data: [33.8,26.1,19.7,13.6,8.4,6.1,3.7,4.7,5.2,5.4,5.6,5.3,4.6,3.7,2.7,1.8,1.3,0.9,0.6,0.3,0.3,0.2]},
                {name: '华北累计百分比',type: 'line',yAxisIndex: 1,
                data: [25.3,44.7,59.4,69.6,75.9,80.4,83.2,84.9,86.5,88,89.5,91,92,93.8,95,96,96.9,97.6,98.2,98.7,99.2,99.6,99.8,100]}
                ]
            };
myChart4.setOption(option4);
/*
var myChart2 = echarts.init(document.getElementById('p1_f2'),theme);
var option2 ={
        grid:{ height:'50%'},
        legend: { type: 'scroll',orient: 'vertical',right: 5,top: 20,
                data: ['Private', 'Taxi','Fleet']
                },
        title:{text: 'Lavida BEV 53Ah',x:'center', y: 'top' },
        toolbox: { show: true,
                feature: {magicType: { saveAsImage: {show:true, title:'保存为图片图'}}}
                },                          
        tooltip: {trigger: 'item'},
        series: [{  name: 'project',
                type: 'pie',
                radius: '55%',
                center: ['40%', '50%'],
                data: [
                        {value: 2438, name: 'Private'},
                        {value: 291, name: 'Taxi'},
                        {value: 4053, name: 'Fleet'},
                        ]  }]
        };
myChart2.setOption(option2);
 
var myChart3 = echarts.init(document.getElementById('p1_f3'),theme);
var option3 ={
                legend: { type: 'scroll',orient: 'vertical',right: 5,top: 20,
                        data: ['Private', 'Taxi','Fleet']
                        },
                title:{text: 'Passat PHEV',x:'center', y: 'top' },
                toolbox: { show: true,
                        feature: {magicType: { saveAsImage: {show:true, title:'保存为图片图'}}}
                        },                          
                tooltip: {trigger: 'item'},
                series: [{  name: 'project',
                        type: 'pie',
                        radius: '55%',
                        center: ['40%', '50%'],
                        data: [
                        {value: 18856, name: 'Private'},
                        {value: 3519, name: 'Fleet'},
                        ]  }]
                };
myChart3.setOption(option3);


var myChart4 = echarts.init(document.getElementById('p1_f4'),theme);
var option4 ={
        legend: { type: 'scroll',orient: 'vertical',right: 5,top: 20,
                data: ['Private', 'Taxi','Fleet']
                },
        title:{text: 'Tiguan L PHEV',x:'center', y: 'top' },
        toolbox: { show: true,
                feature: {magicType: { saveAsImage: {show:true, title:'保存为图片图'}}}
                },                          
        tooltip: {trigger: 'item'},
        series: [{  name: 'project',
                type: 'pie',
                radius: '55%',
                center: ['40%', '50%'],
                data: [
                {value: 13760, name: 'Private'},
                ]  }]
        };
myChart4.setOption(option4);
*/


/*
var myChart5 = echarts.init(document.getElementById("s2_r2"),theme);
var option5 ={legend: { orient: 'vertical',right:"10%",top: '10%',
                        data: ['Lavida BEV 53AH', 'Passat PHEV', 'Tiguan L PHEV']},
                title:{ text: '不同车型地理位置分布',x:'center', y: 'top',},
                toolbox: { show: true,
                        feature: {magicType: {show:true,
                                                title:{line:'切换为折线图',bar:'切换为柱状图'},
                                                type: ['line', 'bar']},
                                                saveAsImage: {show:true, title:'保存为图片图'}
                                                }
                        },
                xAxis: [{ type: 'category',axisTick:{show:true},
                        data: ['东北', '华北', '华东', '华中', "华南",'西北','西南']
                }],
                yAxis: [{type: 'value',min: 0,name:"车辆数目",
                        axisTick:{show:true},
                        axisLine:{show:true},
                        splitLine:{show:false},
                        }],
                tooltip: {trigger: 'axis',axisPointer: { type: 'shadow' }},
                series: [{name: 'Lavida BEV 53AH',type: 'bar',itemStyle:{normal:{barBorderRadius:5}},
                        label: {normal: {show: true,position: 'top'}},
                        data: [1,1029,4590,372,422,110,258] 
                }, 
                        { name: 'Passat PHEV',type: 'bar',barGap: 0,
                        itemStyle:{normal:{barBorderRadius:5}},
                        label: {normal: {show: true,position: 'top'}},
                        data: [774,2929,7499,4341,2738,1278,2816]  }, 
                        { name: 'Tiguan L PHEV', type: 'bar',
                        itemStyle:{ normal:{ barBorderRadius:5 } },
                        label: {  normal: { show: true, position: 'top' } },
                        data: [551,1152,3928,2672,1912,697,1808] }
                        ]
        };
myChart5.setOption(option5);
*/