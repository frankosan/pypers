var m = require('mithril');

var canvas = require('../components/smart-canvas');

var ErrorPage = {
    controller: function() {
        var ctrl = this;

        ctrl.home = function() {
            m.route('/');
        };
    },
    view: function(ctrl) {
        return [
            m('.container container__error',
                m('.message-box',
                    m('div', "It's us not you"),
                    m('.message-body',
                        m('div', 'Could be a server hiccup or just a bug somewhere.'),
                        m('div', 'We have been notified and are working on it :)')
                    ),
                    m('div', {onclick: ctrl.home}, m('i.fa fa-map-signs'), 'Back to safety')
                )
            ),
            m('canvas', {'data-color-shade': 'red', config: canvas.setup})
        ]
    }
};


exports.view = ErrorPage.view;
exports.controller = ErrorPage.controller;
