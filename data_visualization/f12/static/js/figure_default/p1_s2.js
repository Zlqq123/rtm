var theme='essos';

/*
var myChart4 = echarts.init(document.getElementById('s2_r1'),theme);
//异步调用，passat车辆数目在中国地图上的分布
$.get('../static/json/vehicle_province.json',function(data){
        myChart4.setOption({
                title : [{text: 'Lavida BEV',left: '16.67%',textAlign: 'center'},
                        {text: 'Passat PHEV',left: '50%',textAlign: 'center'},
                        {text: 'Tiguan L PHEV',left: '83.33%',textAlign: 'center' }],

                tooltip : {trigger: 'item'},
                visualMap: {min: 0,max: 2000,left: 'left',top: 'bottom'},
                toolbox: {show: true,orient : 'vertical',left: 'right',top: 'center',
                        feature : { mark : {show: true},
                                restore : {show: true, title:'重置'},
                                saveAsImage : {show: true, title:'保存为图片图'}}
                                },
                grid:[],
                series : [{name:'Lavida',type: 'map',mapType: 'china',roam: false,
                        label: {normal: {show: false},emphasis: {show: false}},
                        data:data.Lavida,
                        left: 0,right: '70%',top: '20%',bottom: '15%'
                        },
                        {name:'Passat',type: 'map',mapType: 'china',roam: false,
                        label: {normal: {show: false},emphasis: {show: false}},
                        data:data.Lavida,
                        left: '35%',right: '35%',top: '20%',bottom: '15%'
                        },
                        {name:'Tiguan',type: 'map',mapType: 'china',roam: false,
                        label: {normal: {show: false},emphasis: {show: false}},
                        data:data.Lavida,
                        left: '70%',right: 0,top: '10%',bottom: '10%'
                        }
                        
                        ]
        })
        },'json');
        */

var myChart1 = echarts.init(document.getElementById('s2_r1_1'),theme);
//异步调用，lavida车辆数目在中国地图上的分布
$.get('../static/json/vehicle_province.json',function(data){
     myChart1.setOption({
           title : {text: 'lavida BEV 53Ah 分布',left: 'center'},
           tooltip : {trigger: 'item'},
           visualMap: {min: 0,max: 2000,left: 'left',top: 'bottom'},
           toolbox: {show: true,orient : 'vertical',left: 'right',top: 'center',
                     feature : { mark : {show: true},
                                 dataView : {show: true, readOnly: false, title:'查看数据'},
                                 restore : {show: true, title:'重置'},
                                 saveAsImage : {show: true, title:'保存为图片图'}}
                       },
           series : [{name: 'lavida',type: 'map',mapType: 'china',roam: false,
               label: {normal: {show: false},emphasis: {show: true}},
               data:data.Lavida}]
     })
  },'json');

var myChart2 = echarts.init(document.getElementById('s2_r1_2'),theme);
//异步调用，tiguan车辆数目在中国地图上的分布
$.get('../static/json/vehicle_province.json',function(data){
myChart2.setOption({
        title : {text: 'Tiguan L PHEV 分布',left: 'center'},
        tooltip : {trigger: 'item'},
        visualMap: {min: 0,max: 2000,left: 'left',top: 'bottom'},
        toolbox: {show: true,orient : 'vertical',left: 'right',top: 'center',
                feature : { mark : {show: true},
                                dataView : {show: true, readOnly: false, title:'查看数据'},
                                restore : {show: true, title:'重置'},
                                saveAsImage : {show: true, title:'保存为图片图'}}
                        },
        series : [{name: 'Tiguan',type: 'map',mapType: 'china',roam: false,
                label: {normal: {show:false},emphasis: {show: true}},
                data:data.Tiguan}]
        })
        },'json');

var myChart3 = echarts.init(document.getElementById('s2_r1_3'),theme);
//异步调用，passat车辆数目在中国地图上的分布
$.get('../static/json/vehicle_province.json',function(data){
        myChart3.setOption({
                title : {text: 'Passat PHEV 分布',left: 'center'},
                tooltip : {trigger: 'item'},
                visualMap: {min: 0,max: 2000,left: 'left',top: 'bottom'},
                toolbox: {show: true,orient : 'vertical',left: 'right',top: 'center',
                        feature : { mark : {show: true},
                                        dataView : {show: true, readOnly: false, title:'查看数据'},
                                        restore : {show: true, title:'重置'},
                                        saveAsImage : {show: true, title:'保存为图片图'}}
                                },
                series : [{name: 'passat',type: 'map',mapType: 'china',roam: false,
                        label: {normal: {show: false},emphasis: {show: true}},
                        data:data.Passat}]
                })
        },'json');



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