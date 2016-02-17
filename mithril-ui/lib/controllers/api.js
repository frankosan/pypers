'use strict';

var request = require('request'),
     getent = require('getent'),
        url = require('url'),
         fs = require('fs'),
       mime = require('mime'),
       path = require('path'),
          _ = require('lodash'),
          Q = require('q'),
         ls = require('../sudo-list-dir');

var getUnixUser = function(username) {
  var user = {};

  try {
    var users = getent.passwd(username);
    if(users.length > 0) {
      user = users[0];
    }
  }
  catch(e) {}

  return user;
};

exports.fofnRead = function(req, res) {
    var queryObject = url.parse(req.url, true).query,
        fpath = queryObject.path,
        username = req.user.sAMAccountName;

    res.contentType('text/javascript');

    var lines = [];

    fs.readFile(fpath, {encoding: 'utf-8'}, function(err, data) {
        if(! err) {
            lines = data.split('\n');
            // lines = lines.map(function(line) {
            //    ls.exists(line, username, function(err, exists) {
            //        if(exists) return line;
            //    })
            // });
        }
        res.send(_.compact(lines));
    });

};

exports.fileRead = function(req, res) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      username = req.user.sAMAccountName;

  ls.head(fpath, username, 2*1024*1024 /* 2M */, function(err, txt) {
      try {
          var _json = JSON.parse(txt);
          txt = JSON.stringify(_json, null, 4);
      } catch(e) {}
      res.contentType('text/plain');
      res.end(txt || '__EMPTY__');
  });

};

exports.cssRead = function(req, res) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      username = req.user.sAMAccountName;

  ls.cat(fpath, username, function(err, txt) {
      res.contentType('text/css');
      res.end(txt);
  });

};

exports.htmlRead = function(req, res) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      username = req.user.sAMAccountName;

  ls.cat(fpath, username, function(err, txt) {
      res.contentType('text/html');
      res.end(txt);
  });

};

exports.fileDownload = function(req, res) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      name = path.basename(fpath),
      username = req.user.sAMAccountName,
      mimetype = mime.lookup(fpath);

  res.setHeader('Content-disposition', 'attachment; filename='+name);
  res.setHeader('Content-type', mimetype);

  if(mimetype.match(/^image\//)) {
    ls.od(fpath, username, function(err, data) {
        res.contentType('application/octet-stream');
        res.end(data);
    });
  }
  else {
    ls.cat(fpath, username, function(err, data, size) {
        res.setHeader('Content-length', size);
        res.end(data, 'binary');
    });
  }

  // var filestream = fs.createReadStream(fpath);
  // filestream.pipe(res, 'binary');
};

exports.pdfRead = function(req, res, next) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      username = req.user.sAMAccountName;

  ls.od(fpath, username, function(err, data) {
      res.contentType('text/html');
      res.send('<object data="data:application/pdf;base64,' + data + '" width="100%" height="100%"></object>');
  });
};


exports.pngRead = function(req, res) {
    var queryObject = url.parse(req.url, true).query,
        fpath = queryObject.path,
        embed = queryObject.embed,
        username = req.user.sAMAccountName;

    ls.od(fpath, username, function(err, data) {
        if(embed === 'true') {
            res.contentType('text/html');
            res.end('<img src="data:image/png;base64,' + data + '">');
        }
        else {
            res.contentType('text/plain');
            res.end('data:image/png;base64,' + data);
        }
    });
};


exports.fileCreate = function(req, res) {
  var filePath = req.body.file,
      fileContent = req.body.content;

  fs.writeFile(filePath, fileContent, function(err) {
    if(err) {
      res.send(500, err);
    }
    else {
      res.send(200, filePath + ' saved!');
    }
  });
};

exports.dirCreate = function(req, res) {
  var fpath = req.body.path,
      username = req.user.sAMAccountName;

  ls.mkDir(decodeURI(fpath), username, false, function(err, data) {
    if(err) {
      return res.send(500, err);
    }
    res.send(200, data);
  });
};

exports.dirDelete = function(req, res) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      recursive = queryObject.recursive,
      username = req.user.sAMAccountName;

  ls.rmDir(decodeURIComponent(fpath), recursive, username, function(err, data) {
    if(err) {
      return res.send(500, err);
    }
    res.send(200, data);
  });
};

exports.dirRender = function(req, res) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      username = queryObject.user;

  var _doReadDir = function() {
    // check if is a directory
    ls.isDir(fpath, username, function(err, isDir) {
      if(err) {
        return res.send(500, err);
      }
      // it's a file, then goto its parent directory
      if(! isDir) {
        fpath = fpath.substring(0, fpath.lastIndexOf('/'));
      }
      // list files and dirs under path
      ls.list(fpath, username, function(list) {
        // remove trailing /
        list.path = fpath.replace(/\/$/, '');

        var ret = {};
        ret.path = list.path;
        ret.dirs = [];
        ret.files = [];

        _.each(list.dirs, function(val, idx) {
          ret.dirs.push(val);
        });
        _.each(list.files, function(val) {
          ret.files.push(val);
        });

        // ret.dirs.shift();

        res.render('pages/fs-browser', {
          'data': ret,
          'user': username
        });
      });
    });
  };

  // check tha path exists
  ls.exists(fpath, username, function(err, exists) {
    if(err) {
      return res.send(500, err);
    }
    if(! exists) {
      return res.send(500, {'code': 'ENOENT', 'path': fpath});
    }
    else {
      _doReadDir();
    }
  });
};

exports.dirRead = function(req, res) {
  var queryObject = url.parse(req.url, true).query,
      fpath = queryObject.path,
      // [rdir, wdir, rfile, wfile]
      mode = queryObject.mode,
      force = queryObject.force || false,
      username = req.user.sAMAccountName;

  // replace leading ~ by user unix home
  if(fpath.match('^~')) {
    fpath = fpath.replace(
      /^~/,
      getUnixUser(username).dir
    );
  }

  // replace {{ username }} by username
  if(fpath.match(/\{\{\s*username\s*\}\}/)) {
    fpath = fpath.replace(
      /\{\{\s*username\s*\}\}/,
      getUnixUser(username).name
    );
  }


  var _doReadDir = function() {
    // check if is a directory
    ls.isDir(fpath, username, function(err, isDir) {
      if(err) {
        return res.send(500, err);
      }
      // it's a file, then goto its parent directory
      if(! isDir) {
        fpath = fpath.substring(0, fpath.lastIndexOf('/'));
      }
      // list files and dirs under path
      ls.list(fpath, username, function(list) {
        // remove trailing /
        list.path = fpath.replace(/\/$/, '');

        res.send(200, list);

        // var ret = {};
        // ret.path = list.path;
        // ret.dirs = [];
        // ret.files = [];
        // console.log(list);

        // _.each(list.dirs, function(val) {
        //   ret.dirs.push(val);
        // });
        // _.each(list.files, function(val) {
        //   ret.files.push(val);
        // });
        // ret.dirs.shift();

        // var promises;
        // if(mode === 'wdir') {
        //   promises = _.map(ret.dirs, function(dir, index) {
        //     var fpath = ret.path + (index > 0? '/' + dir.name : '');
        //     var promise = ls.isWritable(fpath, username);

        //     promise.then(function(writable) {
        //       dir.mode = writable? 'w': 'r';
        //     });

        //     return promise;
        //   });
        //   Q.all(promises).done(function() {
        //     res.send(200, ret);
        //   });
        // }
        // else
        // if(mode === 'wfile') {
        //   promises = _.map(ret.files, function(file, index) {
        //     var fpath = ret.path + '/' + file.name;
        //     var promise = ls.isWritable(fpath, username);

        //     promise.then(function(writable) {
        //       file.mode = writable? 'w': 'r';
        //     });

        //     return promise;
        //   });
        //   Q.all(promises).done(function() {
        //     res.send(200, ret);
        //   });
        // }
        // else {
          // res.send(200, ret);
        // }
        // res.send(200, ret);
      });
    });
  };

  // check tha path exists
  ls.exists(fpath, username, function(err, exists) {
    if(err) {
      return res.send(500, err);
    }
    if(! exists) {
      // create a dir on the fly
      if(force) {
        ls.mkDir(decodeURI(fpath), username, true, function(err, data) {
          if(err) {
            return res.send(500, err);
          }
          _doReadDir();
        });
      }
      // return an error
      else {
        return res.send(400, {'code': 'ENOENT', 'path': fpath, 'message': 'The path provided does not exist'});
      }
    }
    else {
      _doReadDir();
    }
  });

};

