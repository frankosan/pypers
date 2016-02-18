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

var utils   = require('../utils');

var NesLayout   = require('../components/neslayout'),
    FileBrowser = require('../components/file-browser'),
    ButtonList  = require('../components/button-list');

var fileBrowser     = m.component(FileBrowser, {onclose: function() {AnnotationPageVM.browsing = false}});
var fileBrowserCtrl = new fileBrowser.controller();

// TODO Add option for export format

var Annotation = {
    config: function(data) {
        data = data || {};

        // defaults. statically for now
        data.subroutines = [
            'call_features_rRNA_SEED',
            'call_features_tRNA_trnascan',
            'call_features_repeat_region_SEED',
            'call_selenoproteins',
            'call_pyrrolysoproteins',
            'call_features_crispr',
            'call_features_CDS_prodigal',
            'call_features_CDS_glimmer3',
            'call_features_CDS_genemark',
            'annotate_proteins_kmer_v2',
            'annotate_proteins_kmer_v1',
            'annotate_proteins_similarity',
            'resolve_overlapping_features',
            'renumber_features',
            'find_close_neighbors'
        ];

        this.name = m.prop('annotation');

        this.choices = m.request({
            method: 'GET',
            url: '/api/pypers/annotation',
            extract: utils.request.authenticate
        });
        // do not serialize this
        this.choices.toJSON = function() {}

        this.subroutines = m.prop(data.subroutines || []); // here you can put defaults
        this.input_fasta = m.prop(data.input_fasta || '');
        this.genus       = m.prop(data.genus       || '');
        this.input_fofn  = m.prop(data.input_fofn  || '');
        this.output_dir  = m.prop(data.output_dir  || '/scratch/' + utils.user.get().sAMAccountName);
    }
};

var AnnotationPageVM = {
    browsing: ''
};


var AnnotationPage = {};

AnnotationPage = {
    controller: function() {
        var ctrl = this;

        ctrl.feedback = m.prop({});
        ctrl.config = m.prop(new Annotation.config()); // new configuration

        ctrl.toggleAnnotation = function(type, name, selected) {
            var list = ctrl.config()[type]();
            if(selected) {
                list.push(name);
            }
            else {
                list.splice(list.indexOf(name), 1);
            }
            ctrl.config()[type](list);
        };

        ctrl.submit = function() {
            m.request({
                method: 'PUT',
                url: '/api/pypers/annotation',
                data: {
                    config: ctrl.config(),
                    user : utils.user.get().sAMAccountName
                },
                extract: utils.request.authenticate
            }).then(
                function(response) {
                    ctrl.feedback({ success: response });
                },
                function(response) {
                    ctrl.feedback({ error: 'Ooops, an error occured' });
                }
            );
        };

        ctrl.browse = function(root, target) {
            var parts = root.split(':');

            fileBrowserCtrl.init(parts[1], parts[0], target);
            AnnotationPageVM.browsing = root;
        };
    },
    view: function(ctrl) {
        return m.component(NesLayout, {
            menu: 'pipelines',
            breadcrumbs: [{label: 'Annotation Pipeline'}],
            main: [ m('.run-form-container', {class: AnnotationPageVM.browsing? 'browsing': ''},
                    m('.annotation',
                        m('.feedback', {
                                class: ctrl.feedback().error
                                       ? 'error'
                                       : ctrl.feedback().success
                                         ? 'success'
                                         : ''
                            },
                            ctrl.feedback().error || ctrl.feedback().success,
                            m('a', {onclick: m.route.bind(null, '/runs/annotation')}, ctrl.feedback().success? 'See list': '')
                        ),
                        m.component(AnnotationChoices, {
                            types: ['subroutines'],
                            defaults: {
                                subroutines: ctrl.config().subroutines()
                            },
                            choices: ctrl.config().choices(),
                            onclick: ctrl.toggleAnnotation
                        }),

                        m('.flexbox-container-column',
                            m('h3','Input Contigs file in fasta format'),
                            m('.input-group',
                                m('span.input-group-btn',
                                    m('button.btn btn-secondary', {
                                        onclick: ctrl.browse.bind(ctrl, 'file:/scratch/'  + utils.user.get().sAMAccountName, ctrl.config().input_fasta)
                                    }, m('i.fa fa-folder-open'), 'Browse')
                                ),
                                m('input.form-control[type=text]', {
                                    'name' : 'input_fasta',
                                    onchange : m.withAttr('value', ctrl.config().input_fasta),
                                    'value' : ctrl.config().input_fasta(),
                                    'placeholder':'file name'}
                                ),
                                m('span.input-group-btn',
                                    m('button.btn btn-secondary', {
                                        onclick: ctrl.config().input_fasta.bind(ctrl, '')
                                    }, m('i.fa fa-times'))
                                )
                            ),
                            m('input.form-control[type=text]', {
                                'name' : 'genus',
                                onchange : m.withAttr('value', ctrl.config().genus),
                                'value' : ctrl.config().genus(),
                                'placeholder':'Genus'}
                            ),
                            m('h3','Or provide contig/genus list file'),
                            m('.input-group',
                                m('span.input-group-btn',
                                    m('button.btn btn-secondary', {
                                        onclick: ctrl.browse.bind(ctrl, 'file:/scratch/'  + utils.user.get().sAMAccountName, ctrl.config().input_fofn)
                                    }, m('i.fa fa-folder-open'), 'Browse')
                                ),
                                m('input.form-control[type=text]', {
                                    'name' : 'input_fofn',
                                    onchange : m.withAttr('value', ctrl.config().input_fofn),
                                    'value' : ctrl.config().input_fofn(),
                                    'placeholder':'list file name'}
                                ),
                                m('span.input-group-btn',
                                    m('button.btn btn-secondary', {
                                        onclick: ctrl.config().input_fofn.bind(ctrl, '')
                                    }, m('i.fa fa-times'))
                                )
                            ),
                            m('h3','Output directory'),
                            m('.input-group',
                                m('span.input-group-btn',
                                    m('button.btn btn-secondary', {
                                        onclick: ctrl.browse.bind(ctrl, 'dir:'+ctrl.config().output_dir(), ctrl.config().output_dir)
                                    }, m('i.fa fa-folder-open'), 'Browse')
                                ),
                                m('input.form-control[type=text]', {
                                    'name' : 'output_dir',
                                    onchange : m.withAttr('value', ctrl.config().output_dir),
                                    'value' : ctrl.config().output_dir(),
                                    'placeholder':'output directory of this run'}
                                ),
                                m('span.input-group-btn',
                                    m('button.btn btn-secondary', {
                                        onclick: ctrl.config().output_dir.bind(ctrl, '')
                                    }, m('i.fa fa-times'))
                                )
                            ),
                            m('.btn btn-primary btn-submit', {
                                onclick: ctrl.submit
                            }, 'Start Run')
                        )
                     ),
                     fileBrowser.view(fileBrowserCtrl))]
        });
    }
};

var AnnotationChoices = {
    view: function(ctrl, args) {
        return m('.flexbox-container-row', args.types.map(function(type) {
            return m('.column1-3', m.component(ButtonList, {
                name: type,
                choices: args.choices,
                defaults: args.defaults[type] || [],
                onclick: args.onclick
            }));
        }));
    }
};


exports.view       = AnnotationPage.view
exports.controller = AnnotationPage.controller

