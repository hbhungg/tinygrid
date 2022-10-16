



function parse_schedule(schedule,instance){

  var num_batteries = 2
  var charge_level = 420
  
  const schedule_array = schedule.split(/\n/);
  const instance_array = instance.split(/\n/);
  var csv_array = []
  var no_buildings = schedule_array[1];
  var k = 0 
  var load_list_rec = []
  var roomsize_list_rec = []
  var duration_list_rec = []
  var load_list_a = []
  var roomsize_list_a = []
  var duration_list_a = []
//Initialise vaues from instance
  for (var j = 0;j < instance_array.length; j++){
    var row = instance_array[j];
    var row_arr = row.split(/ /)
    if (row_arr[0] == "r"){
      load_list_rec.push(parseInt(row_arr[4]))
      roomsize_list_rec.push(row_arr[3])
      duration_list_rec.push(parseInt(row_arr[5]))}
      
    if (row_arr[0] == "a"){
      load_list_a.push(parseInt(row_arr[4]))
      roomsize_list_a.push(row_arr[3])
      duration_list_a.push(parseInt(row_arr[5]))}
  }
  
// Parse values from schedule

  for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)

    if (row_arr[0] == "r"){
      for (var h = 0; h < 4;h++){
        var time_int = parseInt(row_arr[2]) + 672 * h
        var hours = math.floor((time_int % 96)/4) 
        var minutes = (time_int * 15) %60
        var days = math.floor(math.floor(time_int /4) /24)+1
        if (hours < 10){hours = "0" + hours}
        if (minutes == 0){minutes = "00"}
        var num_rooms = parseInt(row_arr[3]);
        for (var j = 0; j < num_rooms;j++){
          var building_no = row_arr[4+j].charAt(0);
          var new_row = {activity_type:"Recurring",
                         activity_id:row_arr[1],
                         time: "OCT " + days +" " +hours+ ":" + minutes,
                         timeofday:hours + ":" + minutes,
                         day:days,
                         time_val: time_int,
                         load: load_list_rec[row_arr[1]],
                         duration: duration_list_rec[row_arr[1]],
                         building_id:building_no};
                      
                      csv_array.push(new_row)}}}
                      
                      
      if (row_arr[0] == "a"){
        var time_int = parseInt(row_arr[2])
        var hours = math.floor((time_int % 96)/4) 
        var minutes = (time_int * 15) %60
        var days = math.floor(math.floor(time_int /4) /24) +1
        if (hours < 10){hours = "0" + hours}
        if (minutes == 0){minutes = "00"}
        var num_rooms = parseInt(row_arr[3]);
        for (var j = 0; j < num_rooms;j++){
          var building_no = row_arr[4+j].charAt(0);
          var new_row = {activity_type:"Once-off",
                         activity_id:row_arr[1],
                         time: "OCT " + days +" " +hours+ ":" + minutes,
                         timeofday:hours + ":" + minutes,
                         time_val: time_int,
                         day:days,
                         load: load_list_rec[row_arr[1]],
                         duration: duration_list_rec[row_arr[1]],
                         building_id:building_no};
                      
                      csv_array.push(new_row)}}
    
    
    
    
    
    
    if (row_arr[0] == "c"){

      
      if(row_arr[3] == 0){var charge_level = charge_level + 15}
      if(row_arr[3] == 2){var charge_level = charge_level - 15}
      var time_int = parseInt(row_arr[2])
      var hours = math.floor((time_int % 96)/4) 
      var minutes = (time_int * 15) %60
      var days = math.floor(math.floor(time_int /4) /24) +1
      if (hours < 10){hours = "0" + hours}
      if (minutes == 0){minutes = "00"}
      
      var new_row = {activity_type: "Charge",
                     time: "OCT " + days +" " +hours+ ":" + minutes,
                     timeofday: hours + ":" + minutes,
                     day: days,
                     time_val: time_int,
                     battery_id:row_arr[1],
                     charge_dec: row_arr[3],
                     battery_level: charge_level
  
                     }

      csv_array.push(new_row)}
      
      


  }  
  
  
  

return(csv_array)}





function fetch_schedule(){
  
  fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/test_schedule.txt')
  .then((response) => response.text())
  .then((data) => {
  fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/phase1_instance_small_0.txt')
  .then((response) => response.text())
  .then((data2) => {
    var sl = document.getElementById("myRange");
    var schedule_array = parse_schedule(data,data2);
    make_table(schedule_array,sl.value);

    
    })
  
})

}




function make_table(schedule_array,day_num){
  building_id = [0,1,3,4,5,6]
  for (var i = 0; i< 6; i++){
    var t_id = "t" + building_id[i]
    var tableId = document.getElementById(t_id);
    var tBody = tableId.getElementsByTagName('tbody')[0];
    tBody.remove();
    let new_body = document.createElement('tbody')
    tableId.appendChild(new_body)
  }

  
  for (let element in schedule_array){
    
    var entry = schedule_array[element]
    if (entry.day == day_num && (entry.activity_type == "Recurring" | entry.activity_type == "Once-off")){
      var t_id = "t" + entry.building_id
      var tableId = document.getElementById(t_id);
      var tBody = tableId.getElementsByTagName('tbody')[0];
  
      let row_2 = document.createElement('tr');
      let row_2_data_1 = document.createElement('td');
      row_2_data_1.innerHTML = entry.activity_type;
      let row_2_data_2 = document.createElement('td');
      row_2_data_2.innerHTML = entry.activity_id;
      let row_2_data_3 = document.createElement('td');
      row_2_data_3.innerHTML = entry.time;
      row_2.appendChild(row_2_data_1);
      row_2.appendChild(row_2_data_2);
      row_2.appendChild(row_2_data_3);
      tBody.appendChild(row_2);}
}


}
function make_header(){
var building_id = [0,1,3,4,5,6]
for (var i = 0; i < 6; i++) {
  let table = document.createElement('table');
  table.className = "table table-dark"
  table.id = "t" + building_id[i]
  let thead = document.createElement('thead');
  let tbody = document.createElement('tbody');
  table.appendChild(thead);
  table.appendChild(tbody);
  var element_id = "table_"+building_id[i]
  document.getElementById(element_id).appendChild(table)
  let row_1 = document.createElement('tr');
  row_1.className ="row_entry"
  let heading_1 = document.createElement('th');
  heading_1.innerHTML = "Activity Type";
  let heading_2 = document.createElement('th');
  heading_2.innerHTML = "Activity ID";
  let heading_3 = document.createElement('th');
  heading_3.innerHTML = "Time";
  row_1.appendChild(heading_1);
  row_1.appendChild(heading_2);
  row_1.appendChild(heading_3);
  thead.appendChild(row_1);}
  
}
function battery_chart() {
async function fetch_gridload() {
  const [scheduleResponse, instanceResponse] = await Promise.all([
    fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/test_schedule.txt'),
    fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/phase1_instance_small_0.txt')
  ]);
  const schedule = await scheduleResponse.text();
  const instance = await instanceResponse.text();
  return [schedule, instance];
}
fetch_gridload().then(([schedule, instance]) => {
        var sl_val = document.getElementById("myRange").value;
        var csv_array = calc_load(schedule,instance,sl_val)
        
        document.getElementById("demo").innerHTML = "OCT: " + sl_val
        
        
        var dat_val = csv_array
        var capacity_chart = {
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        title:"Battery Capacity" + " October " + sl_val,
        width: 800,
        data: {
          values: dat_val
        },
        mark: 'bar',
        encoding: {x: {field: 'battery_time', timeunit: 'nominal',axis: {title:'Time'}},
        y: {field: 'charge_level',type: 'quantitative',axis: {title: 'Battery Capacity (KwH)'}}
        }
      };
      
      
      
        var load_chart = {
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        title:"Total Grid Load" + " October " + sl_val,
        width: 800,
        data: {
          values: dat_val
        },
        mark: 'line',
        encoding: {x: {field: 'time', timeunit: 'minute'},
        y: {aggregate:'sum',field:'grid_load',type: 'quantitative',axis: {title: 'Load KW'}}
        }
      };

      // Embed the visualization in the container with id `vis`
      vegaEmbed('#battery_capacity', capacity_chart);
      vegaEmbed('#grid_load', load_chart);

}).catch(error => {
  
});


  
function calc_load(schedule,instance,sl_val){
  var charge_level = 420
  
  const schedule_array = schedule.split(/\n/)
  const instance_array = instance.split(/\n/)
  
  var day_num = sl_val
  var grid_load = 0
  var gridload_array = [] 
  var charge_array = []
  var load_list_rec = []
  var duration_list_rec = []
  var load_list_a = []
  var duration_list_a = []
  
   for (var j = 0;j < instance_array.length; j++){
    var row = instance_array[j];
    var row_arr = row.split(/ /);
    if(row_arr[0] == "r"){
      load_list_rec.push(parseInt(row_arr[4]))
      duration_list_rec.push(parseInt(row_arr[5]))
      
    }
    
    if(row_arr[0] == "a"){
      load_list_a.push(parseInt(row_arr[4]))
      duration_list_a.push(parseInt(row_arr[5]))
      
    } 
     
   }
   
   for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)
    var time_int = parseInt(row_arr[2]);
    var day = math.floor(math.floor(parseInt(row_arr[2])/4)/24) + 1;
    if(row_arr[0] == "c"){
         var time_int = parseInt(row_arr[2]);
         var hours = math.floor((time_int % 96)/4) ;
         var minutes = (time_int * 15) %60;
         var day = math.floor(math.floor(time_int/4)/24)+1;
         if (hours < 10){hours = "0" + hours}
         if (minutes == 0){minutes = "00"}
         var time = hours + ":" + minutes
         
      
        if(row_arr[3] == 0){var grid_load = 19.36;
                            var charge_level = charge_level + 15}
         
        if(row_arr[3] == 2){var grid_load = -11.62;
                             var charge_level =charge_level - 15}

         var gridload_row = {battery_time:hours + ":" + minutes,
                             time:hours + ":" + minutes,
                             charge_level: charge_level,
                             grid_load: grid_load}
        if(day == day_num){gridload_array.push(gridload_row)}
      
         
          
        

      
      
    }
    
    
    if(row_arr[0] == "r"){
      
      activity_duration = duration_list_rec[row_arr[1]]
      for(var h = 0; h < 4; h++){
        for(var k= 0; k<activity_duration;k++){
          var time_int = parseInt(row_arr[2]) + 672 * h + k
          var hours = math.floor((time_int % 96)/4) 
          var minutes = (time_int * 15) %60
          var day = math.floor(math.floor(time_int /4) /24) +1
          if (hours < 10){hours = "0" + hours}
          if (minutes == 0){minutes = "00"}
          var num_rooms = parseInt(row_arr[3])
          var new_row = {time:hours + ":" + minutes,
                         grid_load: load_list_rec[row_arr[1]] * num_rooms}
          
          if(day == day_num){gridload_array.push(new_row)} 
          }
            
          }
          
        }

    
    
    
    
    
  }
    
    

         


    
  

        

  arr = gridload_array
          

  
  
     
  
  return(arr)}
      
      



}




async function fetch_forecast() {
  const response = await fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/cache/final_forecast.json');
  const full_forecast = await response.json();
  return full_forecast;

}
function get_forecast() {

fetch_forecast().then(full_forecast => {
  var forecast_arr = forecast_parse(full_forecast)
  var sl_val = document.getElementById("myRange").value;
  var solar_arr = forecast_arr[0]
  var building_arr = forecast_arr[1]
  var solar = solar_arr[sl_val-1]
  var building = building_arr[sl_val-1]
  
  
  var solar_chart = {
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        title:"Solar Production" + " October " + sl_val,
        width: 800,
        data: {
          values: solar
        },
        mark: 'line',
        encoding: {x: {
          axis:{labels: false },
          
          field: 'time', 
          timeunit: 'minute'},
        y: {field: 'power_load',type: 'quantitative',axis: {title: 'KW'}},
        color: {field: 'item_id',type: 'nominal'}
        }
      }
      
      
  var building_chart = {
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        title:"Building Energy Demand" + " October " + sl_val,
        width: 800,
        data: {
          values: building
        },
        mark: 'line',
        encoding: {x:{
        axis:{labels: false }, 
        field: 'time', timeunit: 'minute'},
        y: {field: 'power_load',type: 'quantitative',axis: {title: 'KW'}},
        color: {field: 'item_id',type: 'nominal'}
        }
      }
  
  vegaEmbed('#solar_forecast', solar_chart);
  vegaEmbed('#building_forecast', building_chart);
  
  
  
})

}
function forecast_parse(full_forecast){
  full_arr_solar = []
  full_arr_building = []

  for (var i= 0;i < 31; i++){
    day_array_solar = []
    day_array_building = []
    for (var key in full_forecast){

      all_entries = []
      start_index = i * 96
      end_index = (i+1) * 96
      var fc_list = full_forecast[key]
      slice_forecast = fc_list.slice()
      for (var j = start_index; j < end_index; j++ ){
        var time_int = j+48
        var hours = math.floor((time_int % 96)/4)
        var minutes = (time_int * 15) %60
        var days = math.floor(time_int / 96) +1
        if (hours < 10){hours = "0" + hours}
        if (minutes == 0){minutes = "00"}
        row_entry = {day: days,
                    item_id: key,
                    time:hours + ":" + minutes ,
                    power_load: slice_forecast[j]}
        
        
        
        if (key.includes("Building") == true){day_array_building.push(row_entry)}
        if (key.includes("Solar") == true){day_array_solar.push(row_entry)}
      }}
      full_arr_solar.push(day_array_solar)
      full_arr_building.push(day_array_building)
    
  }
  var total_arr = [full_arr_solar , full_arr_building]
  return total_arr
}






