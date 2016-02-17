var m = require('mithril'),
    $ = jQuery = require('jquery');

var ButtonList = {
    controller: function(args) {
        var ctrl = this;

        ctrl.toggle = function(e) {
            var btn = $(e.target);

            btn.toggleClass('selected');
            // btn.toggleClass('');

            (args.onclick || function() {})(btn.attr('name'), btn.attr('label'), btn.hasClass('selected'));
        };
    },
    view: function(ctrl, args) {
        // replace snake_case by Capital Case
        var _label = args.name.replace(/_([a-z])/g, function (g) {return ' ' + g[1].toUpperCase();});
            _label = _label.charAt(0).toUpperCase() + _label.slice(1);

        return (
            m('.panel panel-default',
                m('.panel-heading', _label),
                m('.panel-body',
                    m('ul.list-group checked-list-box',
                        args.choices.map(function(choice) {
                            return (
                                m('.step-choice', {
                                    class: args.defaults.indexOf(choice) > -1
                                           ? 'selected'
                                           : '',
                                    label: choice,
                                    name: args.name,
                                    onclick: ctrl.toggle
                                }, choice)
                            );
                        })
                    )
                )
            )
        );
    }
};

exports.view = ButtonList.view;
exports.controller = ButtonList.controller;

