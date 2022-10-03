
function parse_schedule(schedule){

  
  var schedule = schedule
  var schedule_array = schedule.split(/\n/);
  var csv_array = []
  var no_buildings = schedule_array[1];
  for (var i = 0; i < schedule_array.length; i++) {
    var row = schedule_array[i];
    var row_arr = row.split(/ /)
    if (row_arr[0] == "r"){
      var num_rooms = parseInt(row_arr[3]);
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






function myFunction() {
  
  
    fetch('https://raw.githubusercontent.com/hbhungg/tinygrid/main/website/schedule/schedule_small.txt')
  .then((response) => response.text())
  .then((data) => {
    var sl = document.getElementById("myRange")
    var schedule_array = parse_schedule(data);
    make_table(schedule_array,sl.value);
  

 
  
  })
  
}


function make_table(schedule_array,day_num){

  
  for (let element in schedule_array){
    
    var entry = schedule_array[element]
    if (entry.day == day_num){
    var t_id = "t" + entry.building_id
    var tableId = document.getElementById(t_id);
  var tBody = tableId.getElementsByTagName('tbody')[0];
  
  let row_2 = document.createElement('tr');
  let row_2_data_1 = document.createElement('td');
  row_2_data_1.innerHTML = "recurring";
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

  
  
  
  
function make_header(schedule_array){
for (var i = 0; i < 6; i++) {
  let table = document.createElement('table');
  table.className = "table table-dark"
  table.id = "t" + i

  let thead = document.createElement('thead');
  let tbody = document.createElement('tbody');
  table.appendChild(thead);
  table.appendChild(tbody);
  var element_id = "table_"+i
  document.getElementById(element_id).appendChild(table)
  let row_1 = document.createElement('tr');
  row_1.className ="row_entry"
  let heading_1 = document.createElement('th');
  heading_1.innerHTML = "Activity ID";
  let heading_2 = document.createElement('th');
  heading_2.innerHTML = "Activity_type";
  let heading_3 = document.createElement('th');
  heading_3.innerHTML = "Time";
  row_1.appendChild(heading_1);
  row_1.appendChild(heading_2);
  row_1.appendChild(heading_3);
  thead.appendChild(row_1);}
  
}


   
function remove_table(){

  
  for (var i = 0; i< 6; i++){
    var t_id = "t" + i
    var tableId = document.getElementById(t_id);
    var tBody = tableId.getElementsByTagName('tbody')[0];
    tBody.remove();
    let new_body = document.createElement('tbody')
    tableId.appendChild(new_body)
  }
}
   

