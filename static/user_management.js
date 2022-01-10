function process_form(String) {
   var prolonged;
   var checked_boxes = getCheckedBoxes("mycheckbox");
   // var numRows = document.getElementById("num-rows");

   var server_data = [
      { "checkbox_type": String },
      { "ids": checked_boxes },
   ];
   console.log("checked_boxes:");
   console.log(checked_boxes);

   $.ajax({
      type: "POST",
      url: "/user_management",
      data: JSON.stringify(server_data),
      contentType: "application/json",
      dataType: 'json',
      success: function (result) {
         // console.log(result.rows);
         for (var i = 0; i < checked_boxes.length; i++) {
            var update = document.getElementById(checked_boxes[i]);
            if (String == 'add') {
               update.innerHTML = "Yes";
            }
            else{
               update.innerHTML = "No";
            }
         }
      }
   });
}

function getCheckedBoxes(chkboxName) {
   var checkboxes = document.getElementsByName(chkboxName);
   var checkboxesChecked = [];
   // loop over them all
   for (var i = 0; i < checkboxes.length; i++) {
      // And stick the checked ones onto an array...
      if (checkboxes[i].checked) {
         checkboxesChecked.push(checkboxes[i].value);
      }
   }
   // Return the array if it is non-empty, or null
   return checkboxesChecked;
}