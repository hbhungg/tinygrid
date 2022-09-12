
var fs = require('fs');


const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const csvWriter = createCsvWriter({
  path: 'out.csv',
  header: [
    {id: 'activity_type', title: 'activity type'},
    {id: 'activity_id', title: 'activity id'},
    {id: 'time', title: 'time'},
    {id: 'building_id', title: 'building_id'},
  ]
});


const buffer = fs.readFileSync("schedule_small.txt");

const schedule = buffer.toString();

const schedule_array = schedule.split(/\n/);

var csv_array = []

var no_buildings = schedule_array[1];



for (var i = 0; i < schedule_array.length; i++) {
   var row = schedule_array[i];
   var row_arr = row.split(/ /)
   if (row_arr[0] == "r"){
      
      var num_rooms = parseInt(row_arr[3]);
      
      for (var j = 0; j < num_rooms;j++){
        var building_no = row_arr[4+j].charAt(0);
        var new_row = {activity_type:row_arr[0],
                       activity_id:row_arr[1],
                       time:row_arr[2],
                       building_id:building_no};
        csv_array.push(new_row)
        
      }}
    
}

csvWriter
  .writeRecords(csv_array)
  .then(()=> console.log('The CSV file was written successfully'));