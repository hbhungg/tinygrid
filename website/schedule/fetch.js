const fetch = require('node-fetch')
const math = require('mathjs')

function parse_schedule(schedule,day_num){
  var min_step = (day_num) * 24 * 4
  var max_step = (day_num+1) *24 *4
  
  var schedule = schedule
  const schedule_array = schedule.split(/\n/);
  var csv_array = []
  var no_buildings = schedule_array[1];
  for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)
    if (row_arr[0] == "r"){var num_rooms = parseInt(row_arr[3]);
      for (var j = 0; j < num_rooms;j++){
        var building_no = row_arr[4+j].charAt(0);
        var hours = math.floor((row_arr[2] % 96)/4) 
        var minutes = (row_arr[2] * 15) %60
        var days = math.floor(math.floor(row_arr[2] /4) /24)

        var new_row = {activity_type:row_arr[0],
                      activity_id:row_arr[1],
                      time: "OCT" + days +" " +(hours)+ ":" + minutes,
                      day:days,
                      building_id:building_no};
                      
                      csv_array.push(new_row)}}}
          
          
        return(csv_array)};



function fetch_schedule(){
  
  fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/website/schedule/schedule_small.txt')
  .then((response) => response.text())
  .then((data) => {var schedule_array = parse_schedule(data,7);
  make_table(schedule_array);
  })
  
}
  
  
  
function make_table(schedule_array){

console.log(schedule_array)}


fetch_schedule()
