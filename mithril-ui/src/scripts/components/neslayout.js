var m = require('mithril');

var Observable = require('../utils/observable'),
    utils      = require('../utils');

var sidebar = require('./sidebar');


var NesLayout = {
    controller: function() {
        var ctrl = this;

        ctrl.feedback = m.prop({});
        ctrl.showFeedback = m.prop(false);

        ctrl.scrollValue = 0;
        ctrl.scrollContent = function(elt) {
            ctrl.scrollValue = elt.scrollTop;
            Observable.trigger('pypers.content.scroll', {
                top: elt.scrollTop
            });
        };

        var feedbackTimeOut = null;
        ctrl.onfeedback = function(args) {
            ctrl.feedback({
                msg  : args.msg,
                level: args.level
            });
            ctrl.showFeedback(true);

            feedbackTimeOut = window.setTimeout(function() {
                ctrl.nofeedback();
                m.redraw();
            }, 5000);
        };
        ctrl.nofeedback = function() {
            ctrl.showFeedback(false);
            ctrl.feedback({});
        };
        Observable.on(['pypers.feedback'], ctrl.onfeedback);
    },
    view: function(ctrl, args) {
        return (
            m('.wrapper',
                m.component(sidebar, {menu: args.menu}),
                m('.page--main',
                    m('.feedback.' + ctrl.feedback().level, {
                            class: ctrl.showFeedback()? 'show': ''
                        },
                        m('a.cls', {onclick: ctrl.nofeedback}, m('i.fa.fa-times')),
                        m('.msg', ctrl.feedback().msg)
                     ),
                    m('header.page--header', {class: ctrl.scrollValue > 0? 'pop': ''},
                        function() {
                            if(args.breadcrumbs.length === 0 && args.header) {
                                return m('h2.header-page', m('i.fa fa-home'), m('.header-label', args.header));
                            }
                            else {
                                return m('h2.header-page', m('a', {onclick: function() {m.route('/');}}, m('i.fa fa-home')));
                            }
                        }(),
                        args.breadcrumbs.map(function(b) {
                            if(b.link) {
                                return m('h3.subheader-page', {class: b.css || ''},  m('a', {
                                    onclick: m.route.bind(null, b.link, b.params || {})
                                }, b.label));
                            }
                            else {
                                return m('h3.subheader-page', b.label);
                            }
                        }),
                        m('.user-info', utils.user.displayName())
                    ),
                    m('section.page--content', {onscroll: function(e) {ctrl.scrollContent(e.target)}}, args.main)
                )
            )
        );
    }
};

exports.view = NesLayout.view;
exports.controller = NesLayout.controller;
