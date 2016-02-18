 // This file is part of Pypers.

 // Pypers is free software: you can redistribute it and/or modify
 // it under the terms of the GNU General Public License as published by
 // the Free Software Foundation, either version 3 of the License, or
 // (at your option) any later version.

 // Pypers is distributed in the hope that it will be useful,
 // but WITHOUT ANY WARRANTY; without even the implied warranty of
 // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 // GNU General Public License for more details.

 // You should have received a copy of the GNU General Public License
 // along with Pypers.  If not, see <http://www.gnu.org/licenses/>.

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
