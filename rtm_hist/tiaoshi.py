sql="SELECT deviceid, uploadtime, vehicle_s, runningDifference(vehicle_s), charg_s, runningDifference(charg_s), " \
        " cast(accmiles,'Float32'), socp, runningDifference(socp)  " \
       "FROM ( SELECT deviceid, uploadtime, if(vehiclestatus=='STARTED',1,0) AS vehicle_s, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, " \
        "vehiclespeed, accmiles, if(soc<0,0,soc) AS socp " \
        "FROM ods.rtm_reissue_history " \
        "WHERE  "+"ORDER BY deviceid,uploadtime"