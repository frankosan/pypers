'use strict';

var osuser = process.env.USER;

var spawn = require('child_process').spawn,
     exec = require('child_process').exec,
        Q = require('q');

var spawnCmd = function (cmd, args, onResponse, onEnd) {
var prcss = spawn(cmd, args);

prcss.stdout.setEncoding('utf8');

prcss.stdout.on('data', function (data) {
    var str = data.toString().trim(),
        lines = str.split(/(\r?\n)/g);

    for (var i=0; i<lines.length; i++) {
        if(lines[i].trim()) {
            onResponse(lines[i].trim());
        }
    }
});

prcss.stderr.on('data', function (data) {
    console.log('[ERROR] spawn cmd', cmd, args);
    console.log('!!!!', data.toString());
});

prcss.stdout.on('end', function () {
        onEnd();
    });
};

var sudoYorN = function(user) {
    if(user === osuser) {
        return '';
    }
    else {
        return 'sudo -u ' + user + ' ';
    }
};


// returns boolean
exports.exists = function(path, user, callback) {
    exec(sudoYorN(user) + 'test -e ' + path + ' ; echo $?',
        function(err, stdout, stderr) {
            callback(err, stdout.toString().trim() === '0');
        }
    );
};

// returns a promise
exports.isWritable = function(path, user) {
    var deferred = Q.defer();
    exec(sudoYorN(user) + 'test -w "' + path + '" ; echo $?',
        function(err, stdout, stderr) {
            if(err) {
                deferred.reject(err);
            }
            else {
                deferred.resolve(stdout.toString().trim() === '0');
            }
        }
    );
    return deferred.promise;
};

// returns boolean
exports.isDir = function(path, user, callback) {
    exec(sudoYorN(user) + 'test -d ' + path + ' ; echo $?',
        function(err, stdout, stderr) {
            callback(err, stdout.toString().trim() === '0');
        }
    );
};

exports.rmDir = function(path, recursive, user, callback) {
    var cmd = recursive === '1'? 'rm -rf': 'rmdir';

    exec(sudoYorN(user) + cmd + ' "' + path + '"',
        function(err, stdout, stderr) {
            callback(stderr.toString().trim(), stdout.toString().trim());
        }
    );
};

exports.mkDir = function(path, user, mkParents, callback) {
    exec(sudoYorN(user) + 'mkdir ' + (mkParents? '-p ': '') + '"' + path + '"',
        function(err, stdout, stderr) {
            callback(stderr.toString().trim(), stdout.toString().trim());
        }
    );
};

exports.cat = function(path, user, callback) {
    exports.fileSize(path, user, function(err, size) {
        exec(sudoYorN(user) + 'cat ' + path,
            {encoding: 'utf8', maxBuffer: size},
            function(err, stdout, stderr) {
                callback(err, stdout.toString().trim(), size);
            }
        );
    });
};

exports.od = function(path, user, callback) {
    exports.fileSize(path, user, function(err, size) {
        exec(sudoYorN(user) + 'cat ' + path + ' | base64',
            {encoding: 'utf8', maxBuffer: size},
            function(err, stdout, stderr) {
                var data = stdout.toString().trim();
                callback(err, data);
            }
        );
    });
};


exports.head = function(path, user, limit, callback) {
    // first get the size of the file
    exports.fileSize(path, user, function(err, size) {
        var cmd = "awk '{i += (length() + 1); if (i <= " + limit + ") print $ALL}' " + path;

        exec(sudoYorN(user) + cmd,
            {encoding: 'utf8', maxBuffer: limit},
            function(err, stdout, stderr) {
                var data = stdout.toString().trim();

                // check if file has been truncated
                if(size > limit) {
                    data += '\n\ntruncated file...\n';
                }
                callback(err, data);
            }
        );
    });
};

exports.fileSize = function(path, user, callback) {
    var cmd = "stat --printf %s " + path;
    exec(sudoYorN(user) + cmd,
        {encoding: 'utf8'},
        function(err, stdout, stderr) {
            var data = parseInt(stdout.toString().trim());
            callback(err, data);
        }
    );
};

/**
* calls the callback giving it an object of dirs and files as arrays
*/
exports.list = function(path, user, callback) {
    var dirs = [],
        files = [];

    var cmd = 'sudo';

    function doList(cmd, args, arr, cont) {
        //console.log(cmd, args.join(' '));
        spawnCmd(cmd, args,
            function(ret) {
                arr.push(ret);
            },
            function() {
                cont({dirs: dirs, files: files.sort()});
            }
        );
    }

    if(user === osuser) {
        cmd = 'find';
    }
    else {
        cmd = 'sudo';
    }

    doList(cmd, makeFindArgs(user, path, 'd'), dirs, function() {
        dirs.shift(); // remove the name of the parent directory
        dirs = dirs.sort();
        doList(cmd, makeFindArgs(user, path, 'f'), files, callback);
    });
};

var makeFindArgs = function(user, path, type) {
    var args = [
        path,
        '-maxdepth',
        '1',
        '-type',
        type,
        '-not',
        '-name',
        '.*',
        '-exec',
        'basename',
        '{}',
        ';'
    ];

    if(user !== osuser) {
        args.unshift('-u', user, 'find');
    }

    return args;
};
