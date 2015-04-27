window.onload = function() {
    if (window.navigator.standalone) {
        $('a[target!="_blank"][href]').click(function(e) {
            window.location = e.target.href;
            return false;
        });
    }
}
