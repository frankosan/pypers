var m = require('mithril'),
    _ = require('lodash');

var ParamBrowse = require('./_browse');

var ParamFile = {
    view: function(ctrl, args) {
        return m.component(ParamBrowse, _.extend(args, {type: 'file'}));
    }
};

exports.view = ParamFile.view;
exports.controller = ParamFile.controller;

