var m = require('mithril'),
    _ = require('lodash');

var storage = require('./cookie-storage');


var Utils = {};

// initialize static lists
Utils.init = function() {
    Utils.pipeline.list = m.request({
        method: 'GET',
        url: '/api/pypers/pipelines',
        extract: Utils.request.authenticate
    });
    Utils.user.list = m.request({
        method: 'GET',
        url: '/api/users',
        extract: Utils.request.authenticate
    });
};

// ----------------------------------------
// User Management Utils                  |
// ----------------------------------------


Utils.user = {};

Utils.user.get = function() {
    var userCookie = storage.get('wbuser') || {};
    if(userCookie.sAMAccountName) {
        return userCookie;
    }
    else {
        return {sAMAccountName: Utils.user.username};
    }
};

Utils.user.set = function(username) {
    Utils.user.username = username;
};

Utils.user.remove = function() {
    return storage.remove('wbuser');
};

Utils.user.login = function(user) {
    return m.request({
        method: 'POST',
        url: '/api/session',
        data: {username: user.username(), password: user.password(), groupname: user.groupname()}
    });
};

Utils.user.displayName = function() {
    var username = Utils.user.get().sAMAccountName;
    var curruser = _.find(Utils.user.list(), function(user) {
        return user.sAMAccountName === username;
    });
    return (curruser || {}).displayName || '';
};

Utils.user.logout = function() {
    m.request({
        method: 'DELETE',
        url: '/api/session',
    }).then(
    function() {
        Utils.user.remove();
    }.bind(this)
  );
};

Utils.user.description = function(username) {
    return _.result(_.find(Utils.user.list(), {'sAMAccountName': username}), 'description') || username;
};


// ----------------------------------------
// Request Utils                          |
// ----------------------------------------

Utils.request = {};

// Interceptor
// Verifies that the request has been made
// by an autenticated user
Utils.request.authenticate = function(xhr) {
    if(xhr.status === 401) {
        m.route('/login');
        return '{}';
    }
    if(xhr.status === 500) {
        m.route('/error');
        return '{}';
    }
    return xhr.responseText;
};

// make the ajax request in the background
// used to display ajax spinner
Utils.request.background = function(args) {
    var completed = m.prop(false);
    var success   = m.prop(false);
    var complete = function(data) {
        (args.onsuccess || function() {})(data);
        completed(true);
        success(true);
        return data;
    };

    var fail = function(msg) {
        (args.onerror || function() {})(msg);
        completed(true);
        return value;
    }

    var redraw = function(value) {
        setTimeout(function() {m.redraw()}, 0);
        return value;
    }

    args.background = true;
    args.config = function(xhr) {
        xhr.timeout = 4000;
        xhr.ontimeout = function() {
            complete();
            m.redraw();
        };
    };
    return {
        data: m.request(args).then(complete, fail).then(redraw),
        ready: completed,
        success: success
    }
};


// ----------------------------------------
// Pipeline Utils                         |
// ----------------------------------------

Utils.pipeline = {};

Utils.pipeline.label = function(name) {
    return _.result(_.find(Utils.pipeline.list(), {'name': name}), 'label') || name;
};



// ----------------------------------------
// Date Utils                             |
// ----------------------------------------

Utils.date = {};
Utils.date.monthNames = ["Jan", "Feb", "Mar",
    "Apr", "May", "Jun", "Jul", "Aug", "Sep",
    "Oct", "Nov", "Dec"];

Utils.date.format = function(timestamp) {
    if(! timestamp) return '';

    var time = new Date(timestamp);
    var day  = time.getDate();
    var month = Utils.date.monthNames[time.getMonth()];
    var year  = time.getFullYear();
    var hour  = time.getHours();
    var min   = time.getMinutes();

    min = (''+min).length === 1? '0'+min: min;

    var date_str = day+" "+month+" "+year+" "+hour+":"+min;

    return date_str;
};

Utils.date.formatTdiff = function(tdiff) {
    // Expects a time duration in ms
    var time_str = '';
    if(tdiff) {
        tdiff /= 1000.;
        if ( tdiff < 60 ) {
            time_str = '< 1m';
        } else {
            tdiff = Math.floor((tdiff)/60);
            var min = tdiff>0 ? tdiff%60 : 0;
            tdiff = Math.floor((tdiff-min)/60);
            var hour = tdiff>0 ? tdiff%24 : 0;
            tdiff = Math.floor((tdiff-hour)/24);
            var day = tdiff>0 ? tdiff : 0;

            if ( day > 0 ) { time_str += day+"d "; }
            if ( hour > 0 ) { time_str += hour+"h "; }
            if ( min > 0 ) { time_str += min+"m "; }
        }
    }

    return time_str;
};


// ----------------------------------------
// FilePath Utils                         |
// ----------------------------------------

Utils.filepath = {};
Utils.filepath.name = function(path) {
    if(! path) return '';

    var parts = path.split('/');
    return _.last(parts || []);
};
Utils.filepath.dir = function(path) {
    if(! path) return '';
    return path.substring(0, path.lastIndexOf('/'));
};
Utils.filepath.ellipsis = function(path, length) {
    if(length) {
      var delta = path.length - length;
      if(delta > 0) {
        var p = Math.round((path.length - delta)/2);
        var s = path.substr(0, p);
        var e = path.substr(-1 * p);
        path = s + '...' + e;
      }
    }
    return path;
};


// ----------------------------------------
// Miscellaneous Utils                    |
// ----------------------------------------

Utils.misc = {};
Utils.misc.hiliteText = function selectElementText(e) {
    var elt = e.target,
        doc = window.document;
    if(window.getSelection && doc.createRange) {
        var selection = window.getSelection();
        var range = doc.createRange();
        range.selectNodeContents(elt);
        selection.removeAllRanges();
        selection.addRange(range);
    }
    else
    if(doc.body.createTextRange) {
        var range = doc.body.createTextRange();
        range.moveToElementText(elt);
        range.select();
    }
};

Utils.misc.statusToCss = function(status) {
    switch(status) {
        case 'succeeded'   : return 'status-icon fa fa-check';
        case 'interrupted' : return 'status-icon fa fa-exclamation';
        case 'running'     : return 'status-icon fa fa-cog';
        case 'failed'      : return 'status-icon fa fa-times';
        case 'queued'      : return 'status-icon fa';
        case 'new'         : return 'status-icon';
        default            : return 'status-icon';
    }
};

Utils.misc.isElementInViewport = function(el) {
    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /*or $(window).height() */
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) /*or $(window).width() */
    );
};

Utils.init();

module.exports = Utils;

