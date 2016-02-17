var m = require('mithril'),
    _ = require('lodash'),
    $ = jQuery = require('jquery'),
    cytoscape  = require('cytoscape'),
    cydagre    = require('cytoscape-dagre'),
    dagre      = require('dagre');

cydagre(cytoscape, dagre);

var Observable = require('../utils/observable');

Observable.on(['pypers.run.new.param.focus'], function(args) {
    cy.getElementById(args.step).addClass('hilite');
    // cy.fit();
});
Observable.on(['pypers.run.new.param.blur'], function(args) {
    cy.$('.hilite').removeClass('hilite');
});


var PipelineDag = {
    controller: function(args) {
        var ctrl = this;

        ctrl.zratio = m.prop(1);
        ctrl.zoom = function(delta) {
            ctrl.zratio(ctrl.zratio() + delta);
            var layout = cy.makeLayout(
                DagConfig.getLayout(args.type, ctrl.zratio())
            );
            layout.run();
        };
        ctrl.reset = function() {
            cy.pan({x:0, y:0});
            ctrl.zoom(1 - ctrl.zratio());
            cy.center(document.getElementById('cy'));
        };


        ctrl.render = function(element, isInitialized, context)  {
            if(isInitialized && context.rendered) return;

            context.rendered = true
            $('#cy')
                .cytoscape({
                layout: DagConfig.getLayout(args.type, ctrl.zratio()),
                // zoomingEnabled: false,
                style: cytoscape.stylesheet()
                    .selector('node')
                    .css(DagConfig.getNodeStyle(args.mode))
                    .selector(':selected')
                    .css(DagConfig.getSelectedStyle(args.mode))

                    .selector('node.hilite')
                    .css({
                        'text-background-color': '#ffffdf',
                        'text-background-opacity': 0.8,
                        'background-color': '#ffffaf',
                        'border-width': '1px',
                        'border-color': '#ffffa5',
                        'z-index': 9
                    })
                    .selector('node.hilite:selected')
                    .css({
                        'text-background-color': '#ffffdf'
                    })
                    .selector('edge')
                    .css({
                        'width': 2,
                        'line-color': '#bbb',
                        'target-arrow-shape': 'triangle',
                        'target-arrow-color': '#bbb',
                        'opacity': 1
                    })
                    .selector('edge[succeeded]')
                    .css({
                        'line-color': DagConfig.colors.succeeded,
                        'target-arrow-color': DagConfig.colors.succeeded
                    })
                    .selector('edge[failed]')
                    .css({
                        'line-color': DagConfig.colors.failed,
                        'target-arrow-color': DagConfig.colors.failed
                    })
                    .selector('edge[running]')
                    .css({
                        'line-color': DagConfig.colors.running,
                        'target-arrow-color': DagConfig.colors.running
                    }),

                ready: function() {
                    window.cy = this;

                    cy.elements().unselectify();
                    window.cy.on('tap', 'node', function(e) {
                        node = e.cyTarget;
                        status = node.data()['status'];
                        if(status.toLowerCase() !== 'queued') {
                            (args.onnodeclick || function() {})(node.id());
                        }
                    });
                    window.cy.on('tap', 'edge', function(e) {
                        edge = e.cyTarget;
                        (args.onedgeclick || function() {})(edge.data().bindings);
                    });
                    cy.load(((args.dag || {}).elements || {nodes: [], edges: []}));
                    cy.center(document.getElementById('cy'));
                    cy.zoomingEnabled(false);

                    cy.onRender(function() {
                        // if(! cy._centered) {
                        //     cy.center(document.getElementById('cy'));
                        //     cy._centered = true;
                        // }
                    });
                }
            })
        }
    },

    view: function(ctrl, args) {
        return (
            m('.dag-container',
                m('#cy', {config: ctrl.render}),
                m('.action-bar',
                    m('a', {onclick: ctrl.zoom.bind(ctrl, -.2)}, m('i.fa fa-search-minus')),
                    m('a', {onclick: ctrl.zoom.bind(ctrl,  .2)}, m('i.fa fa-search-plus')),
                    m('a', {onclick: ctrl.reset.bind(ctrl)},     m('i.fa fa-arrows-alt'))
                )
            )
        );
    }
};


var DagConfig = {
    colors: {
        succeeded: '#74e883',
        running: '#61bffc',
        failed: '#e8747c',
        queued: '#bbb',
        interrupted: '#000'
    },
    dimensions: {
        'demultiplexing'        : {w : 550,  h : 600},
        'low_frequency_variant' : {w : 400,  h : 600},
        'exome_mapping'         : {w : 750,  h : 1100},
        'exome_merge'           : {w : 750,  h : 1100},
        '16s_454'               : {w : 900,  h : 1100},
        '16s_miseq'             : {w : 900,  h : 1100},
        'exome_vc'              : {w : 400,  h : 600},
        'faire_seq'             : {w : 400,  h : 600},
        'rna_seq'               : {w : 700,  h : 600},
        'annotation'            : {w : 400,  h : 600},
        'assembly'              : {w : 400,  h : 600}
    },
    getLayout: function(type, zratio) {
        var d = DagConfig.getDimensions(type);
        var _genericType = {
            name: 'breadthfirst',
            directed: true,
            fit: false,
            padding: 10,
            spacingFactor: .3,
            avoidOverlap: true,
            boundingBox: {
                x1: 0,
                y1: 0,
                x2: (d.w - 160) * zratio,
                y2: (d.h - 80 ) * zratio
            }
        };
        if(! DagConfig.dimensions[type]) {
            return _genericType;
        }
        else if(type === 'annotation') {
            return _genericType;
        }
        else if(type === 'assembly') {
            return _genericType;
        }
        else {
            var d = DagConfig.getDimensions(type);
            return {
                name: 'dagre',

                rankDir: 'TB',
                marginx: 20,
                marginy: 20,
                minLen: function(edge) { return 1; },
                edgeWeight: function(edge) { return 1; },

                // general layout options
                fit: false,
                animate: false,
                boundingBox: {
                    x1: 0,
                    y1: 0,
                    x2: (d.w - 160) * zratio,
                    y2: (d.h - 80 ) * zratio
                }
            };
        }
    },
    getDimensions: function(type) {
        var cdimensions = document.getElementById('cy').getBoundingClientRect();
        var tdimensions = DagConfig.dimensions[type] || {w: 400, h: 600};

        return {
            w: Math.min(cdimensions.width , tdimensions.w),
            h: Math.min(cdimensions.height, tdimensions.h)
        };
    },
    getNodeStyle: function(mode) {
        var css = {
            'width': '25px',
            'height': '25px',
            'content': 'data(name)',
            'text-valign': 'middle',
            'text-background-color': 'white',
            'text-background-shape': 'roundrectangle',
            'text-background-opacity': 0.3,
            'font-size': 13,
            'font-family': 'Consolas,Monaco,"Andale Mono",monospace8'
        };

        if(mode === 'monitor') {
            _.assign(css, {
                'pie-size': '100%',
                'background-color': DagConfig.colors.queued,
                'pie-1-background-color': DagConfig.colors.succeeded,
                'pie-1-background-size': 'data(succeeded)',
                'pie-2-background-color': DagConfig.colors.running,
                'pie-2-background-size': 'data(running)',
                'pie-3-background-color': DagConfig.colors.failed,
                'pie-3-background-size': 'data(failed)'
            });
        }
        else{
            if(mode === 'new') {
                _.assign(css, {
                    'background-color': 'whitesmoke',
                    'border-width': 1,
                    'border-color': '#bbb'
                });
            }
        }
        return css;
    },
    getSelectedStyle: function(mode) {
        if(mode === 'monitor') {
            return {
                'line-color': 'orange',
                'target-arrow-color': 'orange',
                'text-background-color': 'orange'
            };
        }
        else {
            return {};
        }
    }
};


exports.view = PipelineDag.view;
exports.controller = PipelineDag.controller;

