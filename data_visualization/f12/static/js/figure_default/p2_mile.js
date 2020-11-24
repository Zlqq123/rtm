var theme='essos';


var myCharts1 = echarts.init(document.getElementById('mile_f1'),theme);
$.get('../static/json/mile.json',function(data){
    myChart1.setOption({
        title : {text: 'Lavida 每日行驶里程',left: 'center'},
        legend: { orient: 'vertical',right:"10%",top: '10%',
                data: ['March', 'June','March_acc', 'June_acc']},
        toolbox: { show: true,
            feature: {magicType: {show:true,
                                dataView: {show: true, readOnly: false, title:'查看数据'},
                                title:{line:'切换为折线图',bar:'切换为柱状图'},
                                type: ['line', 'bar']},
                                saveAsImage: {show:true, title:'保存为图片图'},
                                restore: {show: true, title:'重置'}
                                    }
            },
        xAxis: [{ type: 'category',axisTick:{show:true},
            data: data.index
            }],
        yAxis: [{type: 'value',min: 0,name:"占比",
            interval: 0.02,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
            {type: 'value',min: 0,name:"累计百分比",
            interval: 0.02,axisLabel: {formatter: '{value} %'},
            axisTick:{show:true},axisLine:{show:true},splitLine:{show:false}},
        ],
        series: [
                {name:"March",type: 'bar',itemStyle:{normal:{barBorderRadius:5}},
                    label: {normal: {show: true,position: 'top'}},
                    data:data.daily_mile_March.lavida},
                {name:"June",type: 'bar',itemStyle:{normal:{barBorderRadius:5}},
                    label: {normal: {show: true,position: 'top'}},
                    data:data.daily_mile_June.lavida},
                {name:"March_acc",type: 'line',yAxisIndex: 1,
                    label: {normal: {show: true,position: 'top'}},
                    data:data.daily_mile_March.lavida_acc},
                {name:"June_acc",type: 'line',yAxisIndex: 1,
                    label: {normal: {show: true,position: 'top'}},
                    data:data.daily_mile_June.lavida_acc},
                ]
        })
    },'json');