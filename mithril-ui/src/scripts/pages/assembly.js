var m = require('mithril');

var utils   = require('../utils');

var NesLayout   = require('../components/neslayout'),
    FileBrowser = require('../components/file-browser'),
    ButtonList  = require('../components/button-list');

var fileBrowser     = m.component(FileBrowser, {onclose: function() {AssemblyPageVM.browsing = false}});
var fileBrowserCtrl = new fileBrowser.controller();

var Assembly = {
    config: function(data) {
        data = data || {};

        this.name = m.prop('assembly');

        this.choices = m.request({
            method: 'GET',
            url: '/api/pypers/assembly',
            extract: utils.request.authenticate
        });
        // do not serialize this
        this.choices.toJSON = function() {}

        this.pre_assemblers  = m.prop(data.pre_assemblers  || []); // here  you can put defaults
        this.assemblers      = m.prop(data.assemblers      || []);
        this.post_assemblers = m.prop(data.post_assemblers || []);

        this.fastq_r1   = m.prop(data.fastq_r1   || '');
        this.fastq_r2   = m.prop(data.fastq_r2   || '');
        this.input_fofn   = m.prop(data.input_fofn   || '');

        this.output_dir = m.prop(data.output_dir || '');
    }
};

var AssemblyPageVM = {
    browsing: ''
};


var AssemblyPage = {};

AssemblyPage = {
    controller: function() {
        var ctrl = this;

        ctrl.feedback = m.prop({});
        ctrl.config = m.prop(new Assembly.config()); // new configuration

        ctrl.toggleAssembler = function(type, name, selected) {
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
            // console.log(JSON.parse(JSON.stringify(ctrl.config())));
            //TODO some validation of config

            m.request({
                method: 'PUT',
                url: '/api/pypers/assembly',
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
            AssemblyPageVM.browsing = root;
        };
    },
    view: function(ctrl) {
        return (
            m.component(NesLayout, {
                menu: 'pipelines',
                breadcrumbs: [{label: 'Assembly Pipeline'}],
                main: [
                    m('.run-form-container', {class: AssemblyPageVM.browsing? 'browsing': ''},
                        m('.assembly',
                            m('.feedback', {
                                    class: ctrl.feedback().error
                                        ? 'error'
                                        : ctrl.feedback().success
                                            ? 'success'
                                            : ''
                                },
                                ctrl.feedback().error || ctrl.feedback().success,
                                m('a', {onclick: m.route.bind(null, '/runs/assembly')}, ctrl.feedback().success? 'See list': '')
                            ),
                            m.component(AssemblersChoices, {
                                types: ['pre_assemblers', 'assemblers', 'post_assemblers'],
                                defaults: {
                                    pre_assemblers  : ctrl.config().pre_assemblers(),
                                    assemblers      : ctrl.config().assemblers(),
                                    post_assemblers : ctrl.config().post_assemblers()
                                },
                                choices: ctrl.config().choices(),
                                onclick: ctrl.toggleAssembler
                            }),

                            m('.inputs-group',
                            m('h3','Input fastq files'),
                                m('.input-group',
                                    m('span.input-group-btn',
                                        m('button.btn btn-secondary', {
                                            onclick: ctrl.browse.bind(ctrl, 'file:/scratch/'+utils.user.get().sAMAccountName, ctrl.config().fastq_r1)
                                        }, m('i.fa fa-folder-open'), 'Browse')
                                    ),
                                    m('input.form-control[type=text]', {
                                        'name' : 'fastq_r1',
                                        onchange : m.withAttr('value', ctrl.config().fastq_r1),
                                        'value' : ctrl.config().fastq_r1(),
                                        'placeholder':'input fastq file read 1'}
                                    ),
                                    m('span.input-group-btn',
                                        m('button.btn btn-secondary', {
                                            onclick: ctrl.config().fastq_r1.bind(ctrl, '')
                                        }, m('i.fa fa-times'))
                                    )
                                ),
                                m('.input-group',
                                    m('span.input-group-btn',
                                        m('button.btn btn-secondary', {
                                            onclick: ctrl.browse.bind(ctrl, 'file:/scratch/'+utils.user.get().sAMAccountName, ctrl.config().fastq_r2)
                                        }, m('i.fa fa-folder-open'), 'Browse')
                                    ),
                                    m('input.form-control[type=text]', {
                                        'name' : 'fastq_r2',
                                        onchange : m.withAttr('value', ctrl.config().fastq_r2),
                                        'value' : ctrl.config().fastq_r2(),
                                        'placeholder':'input fastq file read 2'}
                                    ),
                                    m('span.input-group-btn',
                                        m('button.btn btn-secondary', {
                                            onclick: ctrl.config().fastq_r2.bind(ctrl, '')
                                        }, m('i.fa fa-times'))
                                    )
                                )
                            ),
                            m('h3','Or provide list file of paired fq filenames'),
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
                                        onclick: ctrl.browse.bind(ctrl, 'dir:/scratch/'+utils.user.get().sAMAccountName, ctrl.config().output_dir)
                                    }, m('i.fa fa-folder-open'), 'Browse')
                                ),
                                m('input.form-control[type=text]', {
                                    'name' : 'output_dir',
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
                        ),
                        fileBrowser.view(fileBrowserCtrl)
                    )
                ]
            })
        );
    }
};

var AssemblersChoices = {
    view: function(ctrl, args) {
        return m('.flexbox-container-row', args.types.map(function(type) {
            return m('.column1-3', m.component(ButtonList, {
                name: type,
                choices: args.choices[type],
                defaults: args.defaults[type] || [],
                onclick: args.onclick
            }));
        }));
    }
};


exports.view       = AssemblyPage.view
exports.controller = AssemblyPage.controller

