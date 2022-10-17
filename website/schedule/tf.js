const fetch = require('node-fetch')
const math = require('mathjs')



function battery_chart() {
async function fetch_gridload() {
  const [scheduleResponse, instanceResponse] = await Promise.all([
    fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/phase2_instance_solution_small_2.txt'),
    fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/phase2_instance_small_2.txt')
  ]);
  const schedule = await scheduleResponse.text();
  const instance = await instanceResponse.text();
  return [schedule, instance];
}
fetch_gridload().then(([schedule, instance]) => {
        var sl_val = 7;
        
        var csv_array = calc_load(schedule,instance,sl_val)
        


}).catch(error => {
  
});


  
function calc_load(schedule,instance,sl_val){
  gridload_array = []
 
  
  
  
  
  const schedule_array = schedule.split(/\n/)
  const instance_array = instance.split(/\n/)
  
  var day_num = sl_val
  var battery_arr = []
  
   for (var j = 0;j < instance_array.length; j++){
    var row = instance_array[j];
    var row_arr = row.split(/ /);

    
    if(row_arr[0] == "c"){
      capacity = parseInt(row_arr[3]);
      max_draw = parseInt(row_arr[4]);
      efficiency = parseFloat(row_arr[5]);
      battery_row = {
        battery_capacity:capacity,
        max_draw: max_draw,
        efficiency: efficiency,
      }
      
      battery_arr.push(battery_row)


    }
     
   }
   
   
   console.log()
   
   for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)
    var time_int = parseInt(row_arr[2])+40;
    var day = math.floor(math.floor(parseInt(row_arr[2])/4)/24) + 1;
    if(row_arr[0] == "c"){
         var time_int = parseInt(row_arr[2])+40;
         var hours = math.floor((time_int % 96)/4) ;
         var minutes = (time_int * 15) %60;
         var day = math.floor(math.floor(time_int/4)/24)+1;
         if (hours < 10){hours = "0" + hours}
         if (minutes == 0){minutes = "00"}
         var time = hours + ":" + minutes
         battery_id = parseInt(row_arr[1])
         grid_load = battery_arr[battery_id]
         
         
         
         if(day == 5){console.log(grid_load.max_draw)}
      
        if(row_arr[3] == 0){var grid_load = (grid_load.max_draw / 4) * (1/grid_load.efficiency)  ;
                            var charge_level = charge_level + 15}
         
        if(row_arr[3] == 2){var grid_load = -(grid_load.max_draw / 4) * grid_load.efficiency;
                             var charge_level =charge_level - 15}

         var gridload_row = {battery_time:hours + ":" + minutes,
                             time:hours + ":" + minutes,
                             charge_level: charge_level,
                             grid_load: grid_load}
        if(day == day_num){gridload_array.push(gridload_row)}
      
         
          
        

      
      
    }
    
    


}
arr = gridload_array
return(arr)}
      
}


battery_chart()