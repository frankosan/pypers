var m = require('mithril');
    _ = require('lodash');

var utils = require('../utils');


var sidebarItems = [
    {
        'title'     : 'Services',
        'route'     : '/services',
        'icon'      : 'i.fa fa-cogs'
    },
    {
        'title'     : 'Pipelines',
        'route'     : '/',
        'icon'     : 'i.fa fa-tasks'
    },
    {
        'title'     : 'Steps',
        'route'     : '/steps',
        'icon'     : 'i.fa fa-circle-o'
    },
    {
        'title'     : utils.user.get().description,
        'route'     : '/login',
        'icon'      : 'i.fa fa-user',
        onclick     : utils.user.logout,
        'action'    : {class: 'fa fa-sign-out'}
    },
    {
        'title'     : 'Info',
        'url'       : 'http://wiki.nihs.ch.nestle.com:8090/display/CGI/CGI+Pipelines+Implementation+Status',
        'icon'      : 'i.fa fa-lightbulb-o'
    }
];

var Sidebar = {

    view: function(ctrl, args) {
        return (
            m(".sidebar",
                m(".sidebar--brand","Pypers"),
                m("ul.nav",
                    _.map(sidebarItems, function(item){
                        return (
                            m("li.sidebar--item",
                                m("a.sidebar--link", {
                                        class: (args.menu || '').toLowerCase() === (item.title || '').toLowerCase() ? 'active': '',
                                        onclick : function(){
                                            if (item.onclick) {
                                                item.onclick();
                                            }
                                            if (item.route) {
                                                m.route(item.route);
                                            } else if (item.url) {
                                                window.open(item.url);
                                            }
                                        }

                                    },
                                    m(item.icon),
                                    m("span.sidebar--link__title", item.title,
                                        m("span.sidebar--link__action", item.action)
                                    )
                                )
                            )
                        )
                    })
                )
            )
        )
    }
}


exports.view = Sidebar.view;
