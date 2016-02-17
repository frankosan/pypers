var m = require('mithril');

var models = require('../models');

var utils = require('../utils');

var canvas = require('../components/smart-canvas');

var LoginPage = {
    controller: function() {
        // remove user cookie
        utils.user.remove();

        var ctrl = this;

        ctrl.groups = [
            { name: 'LdapGroup', label: 'YoutLDAPGroup' }
        ];

        ctrl.user = m.prop(new models.User());
        ctrl.submitting = m.prop(false);
        ctrl.error = m.prop('');

        ctrl.submit = function() {
            ctrl.submitting(true); m.redraw();

            utils.user.login(ctrl.user()).then(
                function(data) {
                    ctrl.submitting(false);
                    utils.init(); // initialize to load users and pipelines list
                    utils.user.set(ctrl.user().username()); // create a tmp user object until the middleware sets the cookie
                                                            // needed since landingpage requires username
                    m.route('/landingpage', {}, true);
                },
                function(error) {
                    ctrl.submitting(false);
                    ctrl.error(error);
                }
            );
        };
    },


    view: function(ctrl) {
        return [
            m("div", {class : "container container__login"},
                m('div', {class: "block__login"},
                    m("h1", {class : "block__login--header"}, "Flock"),
                    m("img", {src: "/images/flock-logo.png", class:"block__login--img", alt:""}),
                    m("form", {
                        onsubmit: function() {return false;},
                        onchange: function(e) {
                            ctrl.user().setProp(e.target.name, e.target.value);
                            ctrl.error('');
                        }},
                        m("div", {class: "form-group"},
                            m('label', {for:"groupname"}, 'Group'),
                            m('select[name=groupname].form-control', {
                                value: ctrl.user().groupname()
                            }, ctrl.groups.map(function(group) {
                                return m('option', {value: group.name}, group.label);
                            }))
                        ),
                        m("div", {class: "form-group"},
                            m('label', {for:"username"}, 'Username'),
                            m('input[name=username].form-control', {
                                type: 'text',
                                autofocus: true,
                                value: ctrl.user().username()
                            })
                        ),
                        m("div", {class: "form-group"},
                            m('label', 'Password'),
                            m('input[name=password].form-control', {
                                type: 'password',
                                value: ctrl.user().password()
                            })
                        ),
                        m('button[type=submit]', {
                            class: "btn btn-primary btn-block",
                            onclick: ctrl.submit,
                            disabled: ctrl.submitting()
                        },
                        'Log in ',
                        m('i', {class: 'fa fa-cog fa-spin', style: {visibility: ctrl.submitting()? 'visible': 'hidden'}})
                        ),
                        m('div', {class: "has-error"},
                        m('p', {class: "help-block"}, ctrl.error())
                        )
                    )
                )
            ),
            m("canvas", {'data-color-shade': 'blue', config: canvas.setup})
        ]
    }
};


exports.view = LoginPage.view;
exports.controller = LoginPage.controller;
