function paid(id) {

    var server_data = [
        { "action": "Pay" },
        { "id": id },
    ];

    $.ajax({
        type: "POST",
        url: "/my_reservations",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function () {
            var update = document.getElementById(`pay_submit${id}`);
            console.log(update);
            update.style.visibility = "hidden";
        }
    }); 

}