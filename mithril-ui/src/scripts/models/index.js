var m = require('mithril'),
    _ = require('lodash');

var utils      = require('../utils');
    Observable = require('../utils/observable');

var Param = function(data) {
    data = data || {};

    if(! data.name) {
        throw 'Attribute name for Param is mandatory';
    }

    this.name     = m.prop(data.name);
    this.descr    = m.prop(data.descr || '');
    this.error    = m.prop('');
    this.multiple = m.prop(data.iterable || false);
    this.value    = m.prop(data.value || (this.multiple()? []: ''));
    this.readonly = m.prop(data.readonly || false);

    // required if no attribute value is provided
    this.required = m.prop(data.value === undefined);

    this.type = m.prop(data.type || 'str'); // default type to string

    switch(this.type()) {
        case 'str':
        case 'ref_genome': break;

        case 'int':
            if(data.value === 0) this.value(0);
            break;
        case 'boolean':
            if(! this.value()) this.value(false);
            break;
        case 'float':
            if(data.value === 0) this.value(0);
            this.precision = m.prop(data.precision || 0.001);
            break;
        case 'enum':
            if((data.options || []).length === 0) {
                console.warn('Attribute options is mandatory for enum param [' + data.name + ']');
            }
            this.options = m.prop(data.options || []);
            break;
        case 'file':
            _pre_val = this.multiple()? _.first(this.value()) || '': this.value();
            this.rdir = m.prop(_pre_val.substr(0, _pre_val.lastIndexOf('/')) || '~');
            break;
        case 'dir':
            _pre_val = this.multiple()? _.first(this.value()) || '': this.value();
            this.rdir = m.prop(data.rdir || _pre_val || '/nihs');
            break;

        default: throw 'Unsupported param type: ' + this.type();
    }
};


var User = function(data) {
    data = data || {};

    this.groupname = m.prop(data.groupname || localStorage.getItem('pypers.user.groupname') || 'youldapgroup');
    this.username  = m.prop(data.username  || localStorage.getItem('pypers.user.username')  || '');
    this.password  = m.prop(data.password  || '');

    this.setProp = function(name, value) {
        this[name](value);
        if(name !== 'password') {
            localStorage.setItem('pypers.user.' + name, value);
        }
    }
};


var RunOutput = function(data) {
    data = data || {};

    this.steps   = m.prop([]);
    this.archive = m.prop(false);

    this.countSelection = function() {
        return _.sum(this.steps(), function(step) {
            return step.countSelection();
        });
    };

    this.selection = function() {
        var zselection = {};
        this.steps().forEach(function(step) {
            var zfiles = step.selection();
            if(zfiles.length) {
                zselection[step.name()] = zfiles;
            }
        });
        return zselection;
    };

    this.capture = function() {
        var archive = this.steps().some(function(step) {
            return ! step.archive();
        });
        this.archive(!archive);
    };

    this.toggle = function() {
        this.archive(!this.archive());

        this.steps().forEach(function(step) {
            step.setArchive(this.archive());
        }.bind(this));
    };

    this.clearAll = function() {
        this.archive(false);

        this.steps().forEach(function(step) {
            step.setArchive(this.archive());
        }.bind(this));
    };

    _.map(data, function(output, sname) {
        output.name   = sname;
        output.bubble = this.capture.bind(this);
        this.steps().push(new RunStepOutput(output));
    }.bind(this));
};

var RunStepOutput = function(data) {
    data = data || {};

    this.name    = m.prop(data.name || '');
    this.dir     = m.prop(data.dir  || '');
    this.archive = m.prop(!!data.archive);
    this.files   = m.prop([]);

    this.toggle = function() {
        this.setArchive(!this.archive());
        (data.bubble || function() {})();
    };

    this.setArchive = function(val) {
        this.archive(val);
        this.files().forEach(function(file) {
            file.archive(this.archive());
        }.bind(this));
    };

    this.capture = function() {
        var archive = this.files().some(function(file) {
            return ! file.archive();
        });
        this.archive(!archive);
        (data.bubble || function() {})();
    };

    this.countSelection = function() {
        return _.sum(this.files(), function(f) {
            return f.archive()? 1: 0;
        });
    };

    this.selection = function() {
        return _.chain(this.files())
                .filter(function(f) { return f.archive(); })
                .map(function(f) { return { 'path': f.path(), 'meta': f.meta() }; })
                .value();
    };

    (data.files || []).forEach(function(file) {
        this.files().push(new RunStepOutputFile({
            bubble: this.capture.bind(this),
            path: file.path,
            meta: file.meta,
            archive: this.archive()
        }))
    }.bind(this));
};

var RunStepOutputFile = function(data) {
    data = data || {};

    this.path    = m.prop(data.path || '');
    this.meta    = m.prop(data.meta || {});
    this.archive = m.prop(!!data.archive);

    this.toggle = function() {
        this.archive(!this.archive());
        (data.bubble || function() {})();
    };

};

var File = function(data) {
    data = data || {};

    this.bytes = m.prop(data.bytes || 0);
    this.path  = m.prop(data.path  || '');
    this.size  = m.prop(data.size  || '0');
};

var Files = function(data) {
    data = data || {};

    this.meta = m.prop((data.meta || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.err = m.prop((data.err || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.html = m.prop((data.html || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.log = m.prop((data.log || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.misc = m.prop((data.misc || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.out = m.prop((data.out || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.pdf = m.prop((data.pdf || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.png = m.prop((data.png || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.txt = m.prop((data.txt || []).map(
        function(file) {
            return new File(file);
        }
    ));
    this.dir = m.prop(data.output_dir || '')
};

var Job = function(data, idx, runId, stepName) {
    data = data || {};

    this.idx      = m.prop(idx === undefined? -1: idx);
    this.runId    = m.prop(runId || 0);
    this.stepName = m.prop(stepName || '');
    this.dir      = m.prop(data.output_dir  || '');
    this.status   = m.prop(data.status || 'Queued');
    this.inputs   = m.prop(data.inputs || [])
    this.outputs  = m.prop(data.outputs || [])
    this.meta     = m.prop(data.meta || '')
    this.params   = m.prop(data.params || '')

    this.files = m.prop(new Files()); // lazy load the files

};

var RunOutputs = function(data) {
    data = m.prop(data || {});
}


var StepConfig = function(data) {
    data = data || {};
    data.args = data.args || {};

    this.name    = m.prop(data.name || '');
    this.url     = m.prop(data.url || '');
    this.version = m.prop(data.version || '');
    this.reqs    = m.prop(data.requirements || {});
    this.inputs  = m.prop(data.args.inputs || []);
    this.desc    = m.prop((data.descr || []).join(' '));
    this.outputs = m.prop(data.args.outputs || []);
    this.cmd     = m.prop((data.cmd || []).join('\n\t'));

    this.inputs  = m.prop((data.args.inputs || []).map(function(input) {
        return new Param(input);
    }));
    this.params  = m.prop((data.args.params || []).map(function(param) {
        return new Param(param);
    }));

    this.error = function(obj) {
        this.params().map(function(param) {
            param.error(obj[param.name()] || '');
        });
        this.inputs().map(function(input) {
            input.error(obj[input.name()] || '');
        });
    };

    this.update = function(name, value) {
        this.params().concat(this.inputs()).map(function(o) {
            if(o.name() === name) {
                return o.error('');
            }
        });
    };
};

var Step = function(data) {
    data = data || {};

    this.runId  = m.prop(data.run_id || -1);
    this.name   = m.prop(data.name || '');
    this.total  = m.prop(data.job_counter || 0); // nb of jobs in step
    this.status = m.prop(data.status || 'Queued');
    // this.step_config = m.prop(data.step_config);

    this.jobs = m.prop((data.jobs || []).map(
        function(job, idx) {
            return new Job(job, idx, this.runId(), this.name());
        }.bind(this)
    ));

    this.getJob = function(idx) {
        if(idx < this.jobs().length && idx > -1) {
            return this.jobs()[idx];
        }
        else {
            return new Job();
        }
    };
};


var Stats = function(data) {
    data = data || {};

    this.failed      = m.prop((data.failed || []).length);
    this.interrupted = m.prop((data.interrupted || []).length);
    this.queued      = m.prop((data.queued || []).length);
    this.running     = m.prop((data.running || []).length);
    this.succeeded   = m.prop((data.succeeded || []).length);
    this.total       = m.prop(data.total || 0)
};


var PipelineStats = function(data) {
    data = data || {};

    this.total  = m.prop(data.total || 0); // total runs of pipeline
    this.name   = m.prop(data.name);

    this.createdAt   = m.prop(utils.date.format((data.created_at   || {}).$date));
    this.runningAt   = m.prop(utils.date.format((data.running_at   || {}).$date));
    this.completedAt = m.prop(utils.date.format((data.completed_at || {}).$date));
    this.execTime    = m.prop(data.exec_time || {});
    this.meta        = m.prop(data.meta || undefined)

    var stats = {}
    stats.failed      = m.prop(data.stats.failed || 0);
    stats.interrupted = m.prop(data.stats.interrupted || 0);
    stats.queued      = m.prop(data.stats.queued || 0);
    stats.running     = m.prop(data.stats.running || 0);
    stats.succeeded   = m.prop(data.stats.succeeded || 0);
    stats.total       = m.prop(data.total || 0);

    this.stats = m.prop(stats);
};

var RunStats = function(data) {
    data = data || {};

    this.runId = m.prop(data.run_id);
    this.total = m.prop(data.total || 0); // total jobs of a run
    this.stats = m.prop(new Stats(data.stats));
};

var RunsStats = function(data) {
    data = data || {};

    this.total     = m.prop(data.total || 0); // total runs
    this.totals    = m.prop(new PipelineStats(data.totals))
    this.user      = m.prop(new PipelineStats(data.user))
    this.pipelines = m.prop((data.pipelines || []).map(
        function(pipeline) {
            return new PipelineStats(pipeline);
        }
    ));
};

var Run = function(data) {
    data = data || {};

    data = _.defaults(data, {
        run_id : 0,
        single_step: false,
        output_dir: '.',
        work_dir: '.',
        name : '',
        user : 'unknown',
        status : 'queued',
        created_at : {},
        running_at : {},
        completed_at : {},
        exec_time : '',
        stats : {},
        config: '{}',
        meta : {
            'project_name' : '',
            'descr' : ''
        }
    });

    this.id     = m.prop(data.run_id);
    this.dir    = m.prop(data.output_dir);
    this.wdir   = m.prop(data.work_dir);
    this.name   = m.prop(data.name);
    this.user   = m.prop(data.user);
    this.status = m.prop(data.status);
    this.isStep = m.prop(data.single_step);

    this.config = m.prop(JSON.parse(data.config));


    // these are for readonly purposes
    // should be ignored by the server on create or update
    this.createdAt   = m.prop(utils.date.format((data.created_at).$date));
    this.runningAt   = m.prop(utils.date.format((data.running_at).$date));
    this.completedAt = m.prop(utils.date.format((data.completed_at).$date));
    this.execTime    = m.prop(data.exec_time ? data.exec_time
                                             : utils.date.formatTdiff(Date.now()-(data.created_at).$date));
    this.stats = m.prop(data.stats)
    this.meta = m.prop(data.meta)

    this.steps = m.prop((data.steps || []).map(
        function(step) {
            return new Step(step);
        }
    ));


    this.getStep = function(name) {
        if(! name) return new Step(); // avoid nullpointer exceptions

        step = _.find(this.steps(), function(step) {
            return step.name() === name;
        });
        return step;
    };

    this.doneJobs = m.prop( _.reduce( _.filter(data.steps, {'status':'succeeded'}),
                                      function(done, step){ return done + step.job_counter}, 0)
                          );


    this.action = function(action) {
        return m.request({
            method: 'PUT',
            url: '/api/pypers/runs/pipelines/' + this.id()
                + '/' + action.toLowerCase()
                + '?user=' + utils.user.get().sAMAccountName,
            extract: utils.request.authenticate
        }).then(
            // success
            function() {
                // window.setTimeout(function() {
                    Observable.trigger('pypers.feedback', {
                        msg  : action.toUpperCase() + " ... Done.",
                        level: 'success'
                    });
                // }, 100);
            },
            // failure
            function(msg) {
                window.setTimeout(function() {
                    Observable.trigger('pypers.feedback', {
                        msg  : "Ooops, couldn't " + action + " run " + this.id() + ".",
                        level: 'error'
                    });
                }, 100);
            }
        );
    };

};


exports.Files     = Files;
exports.Job       = Job;
exports.Step      = Step;
exports.Run       = Run;
exports.RunOutput = RunOutput;
exports.RunsStats = RunsStats;

exports.User      = User;

exports.Param     = Param;
exports.StepConfig = StepConfig;
