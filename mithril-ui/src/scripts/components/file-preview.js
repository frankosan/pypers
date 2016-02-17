var m = require('mithril');

var utils = require('../utils');

var FilePreview = {
    controller: function(args) {
        var ctrl = this;

        ctrl.inpreview = m.prop(''); // the path of the file in preview
        ctrl.content   = m.prop('');
        ctrl.visible   = m.prop(false);

        ctrl.close = function() {
            ctrl.visible(false);
            ctrl.inpreview('');
            // ctrl.content('');
        };

        ctrl.open = function(file) {
            ctrl.content = m.request({
                method: 'GET',
                url: '/api/fs/txt',
                data: {path: file.path()},
                deserialize: function(value) {return value;},
                extract: utils.request.authenticate
            });
            ctrl.inpreview(file.path());
            ctrl.visible(true);
        };

        ctrl.toggle = function(file) {
            if(file.path() === ctrl.inpreview()) {
                ctrl.close();
                return '';
            }
            else {
                ctrl.open(file);
                return file.path();
            }
        };
    },
    view: function(ctrl) {
        return m('.container__file-preview', {class: ctrl.visible()? 'visible': ''},
                   m('a', {onclick: ctrl.close}, m('i.fa fa-times')),
                   m('code', m('pre', ctrl.content() || ''))
               );
    }
};

exports.view = FilePreview.view;
exports.controller = FilePreview.controller;
