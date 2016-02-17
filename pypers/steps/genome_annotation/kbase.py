from pypers.core.step import Step

class KbaseStep(Step):

    extra_env = {
        'KB_TOP' : '/software/pypers/KBaseExecutables/build-Jun022014/deployment',
        'KB_RUNTIME' : '/software/pypers/KBaseExecutables/prod-Nov222013/runtime',
        'PATH' : '/software/pypers/KBaseExecutables/prod-Nov222013/runtime/bin:/software/pypers/KBaseExecutables/build-Jun022014/deployment/bin:/usr/bin:$PATH',
        'PERL5LIB' : '/software/pypers/KBaseExecutables/build-Jun022014/deployment/lib:/software/pypers/KBaseExecutables/build-Jun022014/deployment/plbin:$PERL5LIB'
        }

    perl_bin_path = "/software/pypers/KBaseExecutables/build-Jun022014/deployment/plbin"
