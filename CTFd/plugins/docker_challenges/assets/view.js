CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.data = undefined;

CTFd._internal.challenge.renderer = null;


CTFd._internal.challenge.preRender = function() {}

CTFd._internal.challenge.render = function(markdown) {

    return CTFd._internal.challenge.renderer.render(markdown)
}

String.prototype.format = function () {
  const args = arguments;
  return this.replace(/{([0-9]+)}/g, function (match, index) {     
    return typeof args[index] == 'undefined' ? match : args[index];
  });
};

CTFd._internal.challenge.postRender = function() {}


CTFd._internal.challenge.submit = function(preview) {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val())
    var submission = CTFd.lib.$('#challenge-input').val()

    var body = {
        'challenge_id': challenge_id,
        'submission': submission,
    }
    var params = {}
    if (preview) {
        params['preview'] = true
    }

    return CTFd.api.post_challenge_attempt(params, body).then(function(response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
        }
        return response
    })
};

function nice_text(conn_info, item, port) {
    let copytext = item.host + ' ' + port; // Set the copytext to the desired command format

    if (conn_info.startsWith("ssh")) {
            copytext = conn_info + ' ' + item.host + ' -p ' + port; 
    }
    else if (conn_info.startsWith("http")) {
            copytext = conn_info + '://' + item.host + ':' + port; 
    }
    else if (conn_info.startsWith("nc")) {
            copytext = conn_info + ' ' + item.host + ' ' + port; 
    }

    return copytext;
}


function get_docker_status(container, conn_info = '') {
    CTFd.fetch("/api/v1/docker_status")
        .then((data) => {
            data.json().then((result) => {
                let flag = false;
                CTFd.lib.$.each(result['data'], function(i, item) {
                    if (item.docker_image === container) {
                        flag = true;
                        var ports = String(item.ports).split(',');
                        var data = '';
                        CTFd.lib.$.each(ports, function(x, port) {
                            port = String(port).replace('/tcp', ''); // Remove '/tcp' from the port string
		                    let copytext = nice_text(conn_info, item, port);
                            data = data + '<code id="tocopy">' + copytext + '</code> ';
                            data = data + '<i class="fas fa-copy" onclick="navigator.clipboard.writeText(document.getElementById(\'tocopy\').textContent); alert(\'Copy done\');"></i>';
                            data = data + '<br/>';
                        })
                        CTFd.lib.$('#docker_container').html('<pre>Docker Container Information:<br />' + data + '<div class="mt-2" id="' + String(item.instance_id).substring(0,10) + '_revert_container"></div>');
                        var countDownDate = new Date(parseInt(item.revert_time) * 1000).getTime();
                        var x = setInterval(function() {
                            var now = new Date().getTime();
                            var distance = countDownDate - now;
                            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                            if (seconds < 10) {
                                seconds = "0" + seconds
                            }
                            CTFd.lib.$("#" + String(item.instance_id).substring(0,10) + "_revert_container").html('Next Revert Available in ' + minutes + ':' + seconds);
                            if (distance < 0) {
                                clearInterval(x);
                                CTFd.lib.$("#" + String(item.instance_id).substring(0,10) + "_revert_container").html('<a onclick="start_container(\'' + item.docker_image + '\', \'' + conn_info + '\');" class=\'btn btn-dark\'><small style=\'color:white;\'><i class="fas fa-redo"></i> Revert</small></a>');
                            }
                        }, 1000);
                        return false;
                    };
                });
                if (flag === false) {
                    CTFd.lib.$("#docker_container").html('<a onclick="nuke_container(\'' + container + '\', \'' + conn_info + '\');" class=\'btn btn-danger\'><small style=\'color:white;\'><i class="fas fa-burst"></i> Replace old docker</small></a>');
                }
            }).catch(() => {
                ezal("Attention!", "Error");
            });
        }).catch(() => {
                // TODO
            ezal("Attention!", "Error");
        });
};

function start_container(container, conn_info) {
    CTFd.lib.$('#docker_container').html('<div class="text-center"><i class="fas fa-circle-notch fa-spin fa-1x"></i></div>');
    CTFd.fetch("/api/v1/container?name=" + container )
        .then((data) => {
            console.log(data);
            if (data.status === 409) {
                CTFd.lib.$("#docker_container").html('<a onclick="nuke_container(\'' + container + '\', \'' + conn_info + '\');" class=\'btn btn-danger\'><small style=\'color:white;\'><i class="fas fa-burst"></i> NUKE</small></a>');
            }
            else {
                get_docker_status(container, conn_info);
            }
        }).catch(() => {
            ezal("Attention!", "You can only revert a container once per 5 minutes! Please be patient.");
            get_docker_status(container, conn_info);
        });
}

function nuke_container(container, conn_info) {
    CTFd.lib.$('#docker_container').html('<div class="text-center"><i class="fas fa-circle-notch fa-spin fa-1x"></i></div>');
    CTFd.fetch("/api/v1/container?name=" + container + "&nuke=true")
        .then((data) => {
            get_docker_status(container, conn_info);
        }).catch(() => {
            ezal("Attention!", "Nuke didnt work");
            get_docker_status(container, conn_info);
        });
}

function ezal(title, body) {
    const content =
        '<div>' +
        '<h5>' + title + '</h5>' +
        '<p>' + body + '</p>' +
        '</div>';

    CTFd.lib.$("#docker_container").html(content);
}