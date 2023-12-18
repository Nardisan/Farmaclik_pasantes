$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
    $("#cancel_my_membership").click(function(ev){
        ev.preventDefault();
        var reason = $("#membership_cancel_reason").val()
        console.log("reason", reason, $(this).attr("href"))
        var url = $(this).attr("href") 
        if(url){
            url += "?reason=" +reason
        }
        $.get(url, {"reason":reason}, function(data,status,xhr){
            if(status == "success"){
                location.reload();
            }
            else if(status == "error"){
                alert("Something went wrong! Try after sometime.")
            }
        });
    });
});