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
    _ = require('lodash');

var utils   = require('../utils');

var NesLayout   = require('../components/neslayout')

var ServiceStatus = {
    list: function() {
        return m.request({
            method: 'GET',
            url: '/api/pypers/services',
            extract: utils.request.authenticate
        });
    },
    set: function(name, status){
        return m.request({
            method: 'PUT',
            url: '/api/pypers/services/' + name,
            extract: utils.request.authenticate,
            data: { 'status' : status }
        });
    },
}


ServicePage = {
    controller: function() {
        var ctrl = this;
        ctrl.serviceStatusList = ServiceStatus.list()
        ctrl.toggleStatus = function(name, status){
            ServiceStatus.set(name, ! status)
            ctrl.serviceStatusList = ServiceStatus.list()
        }

    },
    view: function(ctrl) {
        return (
            m.component(NesLayout, {
                menu: 'Services',
                breadcrumbs: [{label: 'Services'}],
                main: [
                    m('ul',
                        _.map(ctrl.serviceStatusList(), function(value, key){
                            return (
                                m('li', {class:'cgi-services'},
                                    m('.cgi-services-label', key),
                                        m('.cgi-services-status switch',
                                        m('input', {
                                            id: 'demultiplexing_toggle_switch', 
                                            checked: value, 
                                            class:'cmn-toggle cmn-toggle-round-flat', 
                                            type:'checkbox',
                                            onclick : ctrl.toggleStatus.bind(ctrl, key, value)}
                                        ),
                                        m('label', {for: 'demultiplexing_toggle_switch'})
                                    )
                                )
                            )
                        })
                    )
                ]
            })
        );
    }
};

exports.view       = ServicePage.view
exports.controller = ServicePage.controller

