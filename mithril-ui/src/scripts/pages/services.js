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

