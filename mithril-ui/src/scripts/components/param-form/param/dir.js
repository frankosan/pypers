var m = require('mithril'),
    _ = require('lodash');

var ParamBrowse = require('./_browse');

var ParamDir = {
    view: function(ctrl, args) {
        return m.component(ParamBrowse, _.extend(args, {type: 'dir'}));
    }
};

exports.view = ParamDir.view;
exports.controller = ParamDir.controller;

