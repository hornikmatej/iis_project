function reserve_js(id) {

    var count = document.getElementById('pocet').value;

    var server_data = { "action": "Reserve", "id": id, "count": count };

    $.ajax({
        type: "POST",
        url: "/r_conf/" + id,
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
    
        success: function () {
            var msg = document.getElementById('msg_reservation');
            msg.style.display = "block";

            var tohide1 = document.getElementById('label_tohide');
            var tohide2 = document.getElementById('div_tohide');
            tohide1.style.display = "none";
            tohide2.style.display = "none";
        }
    }); 
}