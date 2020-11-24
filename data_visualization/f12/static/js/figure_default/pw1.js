
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





