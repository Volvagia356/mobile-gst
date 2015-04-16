window.onload = function() {
    if (window.navigator.standalone) {
        alert("Standalone Mode!");
        $('a[target!="_blank"][href]').click(function(e) {
            window.location = e.target.href;
            return false;
        });
    }
}
