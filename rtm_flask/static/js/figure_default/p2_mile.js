var theme='essos';

var data1={
    index:
     ["0~20", "20~40", "40~60", "60~80", "80~100", "100~120","120~140", "140~160", "160~180", "180~200", "200~220", 
        "220~240", "240~260", "260~280", "280~300", "300~320", "320~340", "340~360", "360~380", "380~400", "400~420",
        "420~440", "440~460", "460~480"], 
    mile_convert:{
        March: [0.02544529262086514, 0.06361323155216285, 0.02544529262086514, 
            0.11450381679389314, 0.10178117048346055, 0.26717557251908397, 
            0.5343511450381679, 1.1323155216284988, 2.4300254452926207, 
            4.8346055979643765, 9.4529262086514, 13.206106870229007, 
            16.463104325699746, 17.150127226463106, 13.944020356234097, 
            9.020356234096692, 4.872773536895674, 2.786259541984733, 
            1.5012722646310432, 0.7251908396946565, 0.5343511450381679, 
            0.44529262086513993, 0.21628498727735368, 0.15267175572519084],
        June: [0.05976240798775599, 0.01311857736316595, 0.0262371547263319, 
            0.010203337949129072, 0.033525253261424096, 0.08308432330005103, 
            0.23176153341593178, 0.5568107280810437, 1.4226368340499962, 
            3.652794985788208, 8.650972961154435, 14.837110997740691, 
            18.943225712411632, 18.675023686320237, 14.246775016398223, 
            9.031411704686247, 4.6658406821660225, 2.246191968515414, 
            1.1077909773340135, 0.5232854748196195, 0.39793018001603386, 
            0.23321915312295022, 0.18511770279134174, 0.16616864660010205]
        },
    daily_mile_March:{
        lavida: [
            39.94569828610216, 21.270999490921433, 13.202104191413541, 8.005260478533854, 
            4.819277108433735, 3.512642117766842, 2.2060071270999493, 1.5696589173595792, 
            1.1920923129136265, 0.9502799932122857, 0.7593755302901748, 0.5854403529611404, 
            0.5811980315628712, 0.33938571186153066, 0.2078737485151875, 0.26302392669268626, 
            0.14848124893941964, 0.13999660614288137, 0.08908874936365178, 0.07211946377057525, 
            0.055150178177498725, 0.0254539283896148, 0.02969624978788393, 0.02969624978788393], 
        tiguan: [
            39.69260164995283, 23.91109722464234, 13.942882550517039, 8.109764524211526, 
            4.622992387144068, 2.822224492125771, 1.8290081656442088, 1.1512416706223074, 
            0.8682381075413539, 0.6351056606721185, 0.43502033900341885, 0.3484969566601975, 
            0.3022309813794471, 0.23553587415654723, 0.18386218747934555, 0.14841163499149787, 
            0.14180220995139067, 0.130986787158488, 0.11836879390010155, 0.10214565971074753, 
            0.07390538908483497, 0.08051481412494217, 0.06609425040107193, 0.047467688924406205],
        passat: [
            37.10277187529732, 22.498493546034062, 13.570771621578764, 8.344169230281311, 
            5.1901303479115795, 3.396657257936634, 2.2220195997589673, 1.6241952364339858, 
            1.2111097015635406, 0.9474802575243411, 0.7425232311058958, 0.6021851511211189, 
            0.4955440677428562, 0.4027782182613936, 0.29732644064571373, 0.27155814912308524, 
            0.2243823538739653, 0.18117091116678824, 0.15897053693190827, 0.1268592813421712, 
            0.11338048269956551, 0.10862325964923408, 0.09633376676921125, 0.07056547524658273], 
        lavida_acc: [
            39.94569828610216, 61.21669777702359, 74.41880196843714, 82.42406244697098, 
            87.24333955540472, 90.75598167317156, 92.96198880027151, 94.53164771763109, 
            95.72374003054472, 96.674020023757, 97.43339555404718, 98.01883590700832, 
            98.60003393857119, 98.93941965043271, 99.1472933989479, 99.41031732564059, 
            99.55879857458001, 99.69879518072288, 99.78788393008654, 99.86000339385713, 
            99.91515357203463, 99.94060750042422, 99.97030375021212, 100.0], 
        tiguan_acc: [
            39.69260164995283, 63.603698874595175, 77.54658142511221, 85.65634594932374, 
            90.2793383364678, 93.10156282859357, 94.93057099423778, 96.0818126648601, 
            96.95005077240144, 97.58515643307356, 98.02017677207698, 98.36867372873718, 
            98.67090471011663, 98.90644058427317, 99.09030277175252, 99.23871440674402, 
            99.3805166166954, 99.5115034038539, 99.629872197754, 99.73201785746475, 
            99.80592324654958, 99.88643806067452, 99.95253231107559, 100.0], 
        passat_acc: [
            37.10277187529732, 59.601265421331384, 73.17203704291015, 
            81.51620627319146, 86.70633662110305, 90.10299387903967, 92.32501347879864, 
            93.94920871523263, 95.16031841679616, 96.1077986743205, 96.85032190542641, 
            97.45250705654752, 97.94805112429039, 98.35082934255178, 98.6481557831975, 
            98.91971393232058, 99.14409628619454, 99.32526719736133, 99.48423773429323, 
            99.61109701563541, 99.72447749833498, 99.83310075798421, 99.92943452475342, 100.0]
    },
    daily_mile_June:{
        lavida: [
            23.285924688399902, 17.363874172913324, 12.484887120529335, 8.357697126904224, 5.451627794508804, 
            3.9172583587962455, 2.833527510936229, 2.4158624782924094, 2.3246356422149437, 2.521377854960322, 
            2.6972368160735094, 2.7423006748587633, 2.7269130157613595, 2.5477566991272997, 2.2092281989844147, 
            1.8168428920006154, 1.3409245784880526, 0.9199621903233606, 0.6429843265700907, 0.5198830537908598, 
            0.3682046998307357, 0.23081488646105822, 0.18465190916884658, 0.09562331010529555], 
        tiguan: [
            31.59605462633119, 23.958599779148912, 15.369114536867784, 9.628857875462446, 5.9536212715782115, 
            3.7310732489440945, 2.3825714802637736, 1.6492086169356601, 1.1844231357111217, 0.9395529325156436, 
            0.6812694570432156, 0.5365308910779903, 0.4666571006120195, 0.3556076836214587, 0.2863577662846483, 
            0.2523566807454036, 0.21367654673745545, 0.17842771493988982, 0.166262188921261, 0.11510459233010374, 
            0.11042554386140034, 0.10200325661773421, 0.0739289658055138, 0.06831410764306971], 
        passat: [
            29.004485179407176, 21.897425897035884, 14.452028081123244, 9.480791731669266, 5.949444227769111, 
            4.013504290171607, 2.8858716848673946, 2.205781981279251, 1.6999804992199687, 1.4430577223088925, 
            1.2426872074882995, 1.0393915756630265, 0.9355499219968798, 0.766380655226209, 0.6513260530421218,
            0.5170144305772231, 0.421948127925117, 0.3268818252730109, 0.27130460218408736, 0.22523400936037444, 
            0.17916341653666146, 0.1479621684867395, 0.13650546021840873, 0.10627925117004679],
        lavida_acc: [
            23.285924688399902, 40.64979886131322, 53.134685981842566, 61.492383108746786, 66.94401090325559, 
            70.86126926205183, 73.69479677298806, 76.11065925128048, 78.43529489349542, 80.95667274845574, 
            83.65390956452924, 86.39621023938801, 89.12312325514937, 91.67087995427667, 93.88010815326109, 
            95.6969510452617, 97.03787562374974, 97.95783781407312, 98.6008221406432, 99.12070519443407, 
            99.4889098942648, 99.71972478072585, 99.9043766898947, 100.0], 
        tiguan_acc: [
            31.59605462633119, 55.5546544054801, 70.92376894234789, 80.55262681781034, 86.50624808938854, 
            90.23732133833263, 92.61989281859641, 94.26910143553206, 95.4535245712432, 96.39307750375885, 
            97.07434696080205, 97.61087785188003, 98.07753495249206, 98.43314263611353, 98.71950040239817, 
            98.97185708314358, 99.18553362988104, 99.36396134482092, 99.53022353374217, 99.64532812607229, 
            99.75575366993368, 99.85775692655142, 99.93168589235692, 100.0], 
        passat_acc: [
            29.004485179407176, 50.901911076443064, 65.3539391575663, 74.83473088923557, 80.78417511700468, 
            84.79767940717629, 87.68355109204367, 89.88933307332293, 91.58931357254289, 93.03237129485179, 
            94.27505850234009, 95.31445007800312, 96.25, 97.01638065522621, 97.66770670826833, 98.18472113884556, 
            98.60666926677068, 98.93355109204369, 99.20485569422777, 99.43008970358814, 99.6092531201248, 
            99.75721528861155, 99.89372074882995, 100.0]
    },
    mile_perchanging_March:{
        lavida: [
            7.479674796747967, 7.92995622263915, 9.055659787367103, 8.48030018761726, 
            10.231394621638525, 10.794246404002502, 10.681676047529706, 9.405878674171356, 
            8.58036272670419, 6.504065040650407, 5.015634771732333, 3.1769856160100063, 
            1.638524077548468, 0.7379612257661038, 0.1125703564727955, 0.0375234521575985, 
            0.06253908692933083, 0.012507817385866166, 0.025015634771732333, 0.012507817385866166, 
            0.0, 0.0, 0.012507817385866166, 0.012507817385866166], 
        tiguan: [
            20.695828897706377, 28.379947740249683, 19.56353430755831, 10.761637472176522, 
            6.029226749249976, 3.900125810510016, 2.5791154553372686, 1.6839252879125133, 
            1.4177876705700183, 1.0742282009097068, 0.7451853285589858, 0.6338914158521243, 
            0.43065905351785544, 0.3774315300493564, 0.2709764831123585, 0.21774895964385946, 
            0.24678215426304073, 0.23710442272331364, 0.17903803348495112, 0.18387689925481468, 
            0.06774412077808963, 0.11613277847672505, 0.08226071808768025, 0.12581051001645216], 
        passat: [
            16.638294487312066, 25.40927531620396, 20.727070241030944, 11.825630419218838, 
            7.057513324317874, 4.500835255747355, 3.0626044069684193, 2.2480311828812343, 
            1.721422321215496, 1.2807254792777027, 1.0023068968260282, 0.8098003341022989, 
            0.6395672579747037, 0.574337761514597, 0.44865165857926975, 0.39455890541723015, 
            0.3388751889268953, 0.28319147243656034, 0.2593270225121311, 0.18614270941054809, 
            0.18932463606713865, 0.15273247951634716, 0.13045899292021318, 0.1193222496221462], 
        lavida_acc: [
            7.479674796747967, 15.409631019387119, 24.465290806754222, 32.94559099437148, 
            43.17698561601001, 53.97123202001251, 64.65290806754221, 74.05878674171356, 
            82.63914946841776, 89.14321450906817, 94.15884928080051, 97.3358348968105, 
            98.97435897435898, 99.71232020012508, 99.82489055659788, 99.86241400875548, 
            99.9249530956848, 99.93746091307067, 99.9624765478424, 99.97498436522827, 
            99.97498436522827, 99.97498436522827, 99.98749218261413, 100.0], 
        tiguan_acc: [20.695828897706377, 49.07577663795607, 68.63931094551438, 
            79.4009484176909, 85.43017516694087, 89.33030097745089, 91.90941643278815, 
            93.59334172070066, 95.01112939127069, 96.0853575921804, 96.83054292073938, 
            97.4644343365915, 97.89509339010935, 98.27252492015872, 98.54350140327107, 
            98.76125036291494, 99.00803251717797, 99.24513693990129, 99.42417497338624, 
            99.60805187264106, 99.67579599341914, 99.79192877189587, 99.87418948998355, 100.0], 
        passat_acc: [16.638294487312066, 42.047569803516026, 62.77464004454697, 
            74.60027046376581, 81.65778378808368, 86.15861904383104, 89.22122345079946, 
            91.46925463368069, 93.19067695489619, 94.4714024341739, 95.47370933099992, 
            96.28350966510222, 96.92307692307692, 97.49741468459152, 97.94606634317078, 
            98.34062524858803, 98.67950043751492, 98.96269190995147, 99.22201893246361, 
            99.40816164187416, 99.5974862779413, 99.75021875745765, 99.88067775037786, 100.0]
    },
    mile_perchanging_June:{
        lavida: [
            5.843566893652554, 6.51012798548826, 7.37680137055326, 8.527087142425247, 10.410158218280761, 
            11.10263313226127, 10.948589856178288, 10.74703790616317, 9.59387282071954, 7.789982868084248, 
            5.388635349332719, 3.132693165949238, 1.556268985473863, 0.5715437439714371, 0.2116295475158722, 
            0.06190524179035718, 0.05182764428960136, 0.04031039000302328, 0.03311210607391198, 0.030232792502267458, 
            0.02735347893062294, 0.01583622464404486, 0.01007759750075582, 0.01871553821568938], 
        tiguan: [
            18.63950853639327, 27.87262659186468, 20.226829356953314, 10.860424820366173, 6.358976844503145, 
            4.033733596675108, 2.7045038713664287, 1.8720692120345575, 1.4407056913327436, 1.1062777932605508, 
            0.8203177065031686, 0.6858195301045693, 0.5937306886064293, 0.4580208169249598, 0.37320214712404126, 
            0.3550267178809873, 0.3174641641120091, 0.2520326188370149, 0.20841158865368536, 0.21931684619951775, 
            0.17569581601618825, 0.17448412073331798, 0.13328648111572902, 0.11753444243841558], 
        passat: [
            15.298103618653238, 23.36360641852148, 19.8280865214186, 11.640236537888413, 7.020061801013286, 
            4.733110598716923, 3.395918623437329, 2.632033002368516, 2.0085329317836025, 1.6085517544272427, 
            1.3324863143695198, 1.192100763885621, 1.0077957115743572, 0.908976832462786, 0.7631013442504666, 
            0.6729095101406992, 0.4917415651028187, 0.44546923282041634, 0.38978557871786423, 0.3427289696171161, 
            0.2650855646008815, 0.23763587595877841, 0.21881323231847913, 0.20312769595156308], 
        lavida_acc: [
            5.843566893652554, 12.353694879140813, 19.730496249694074, 28.25758339211932, 38.66774161040008, 
            49.770374742661346, 60.71896459883964, 71.46600250500282, 81.05987532572236, 88.8498581938066, 
            94.23849354313931, 97.37118670908855, 98.92745569456241, 99.49899943853386, 99.71062898604973, 
            99.77253422784008, 99.82436187212969, 99.8646722621327, 99.89778436820662, 99.92801716070888, 
            99.95537063963951, 99.97120686428356, 99.98128446178431, 100.0], 
        tiguan_acc: [18.63950853639327, 46.512135128257945, 66.73896448521126, 77.59938930557743, 
            83.95836615008058, 87.99209974675568, 90.69660361812211, 92.56867283015667, 94.00937852148942, 
            95.11565631474997, 95.93597402125313, 96.6217935513577, 97.21552423996414, 97.67354505688908, 
            98.04674720401313, 98.40177392189412, 98.71923808600613, 98.97127070484315, 99.17968229349682, 
            99.39899913969636, 99.57469495571254, 99.74917907644586, 99.88246555756159, 100.0], 
        passat_acc: [
            15.298103618653238, 38.66171003717472, 58.48979655859332, 70.13003309648174, 77.15009489749502, 
            81.88320549621194, 85.27912411964927, 87.9111571220178, 89.91969005380139, 91.52824180822863, 
            92.86072812259816, 94.05282888648378, 95.06062459805813, 95.96960143052091, 96.73270277477138, 
            97.40561228491208, 97.8973538500149, 98.34282308283532, 98.73260866155317, 99.0753376311703, 
            99.34042319577118, 99.57805907172997, 99.79687230404843, 100.0]
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
