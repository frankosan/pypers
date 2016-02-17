import inspect
import os
import errno
import jinja2
import sys
import subprocess
import fnmatch
import time
import json
import re
import collections


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def list2cmdline(seq):
    """
    Translate a sequence of arguments into a command line
    string, using the same rules as the MS C runtime:

    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.
    """

    # See
    # http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    # or search http://msdn.microsoft.com for
    # "Parsing C++ Command-Line Arguments"
    result = []
    needquote = False
    for arg in seq:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def import_class(full_name, config_file=None):
    """
    Import the Python class `full_name` given in full Python package format,
    e.g.::

        package.another_package.class_name

    Return the imported class. Optionally, if `subclassof` is not None
    and is a Python class, make sure that the imported class is a
    subclass of `subclassof`.
    """
    # Understand which class we need to instantiate. The class name is given in
    # full Python package notation, e.g.
    #   package.subPackage.subsubpackage.className
    # in the input parameter `full_name`. This means that
    #   1. We HAVE to be able to say
    #       from package.subPackage.subsubpackage import className
    #   2. If `subclassof` is defined, the newly imported Python class MUST be a
    #      subclass of `subclassof`, which HAS to be a Python class.


    if config_file is not None:
        sys.path.insert(0, os.path.dirname(config_file))

    try:
        full_name = full_name.strip()
        package_name, sep, class_name = full_name.rpartition('.')
        class_name = class_name.encode('utf8')
        if not package_name:
            raise ImportError("{0} is not a Python class".format(full_name))
        imported = __import__(
            package_name, globals(), locals(), [class_name, ], level=0)

        step_class = getattr(imported, class_name)

        if not isinstance(step_class, type):
            raise TypeError(
                'Object {0} from package {1} is not a class'.format(
                    class_name, package_name))

    finally:
        if config_file is not None:
            del sys.path[0]

    return step_class



def subproc(cmd, shell=True, env=None):
    """
    Little wrapper to subprocess a comman and get as returned
    values stdout, sterr and rc
    """

    proc = subprocess.Popen(cmd,
                            shell=shell,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    (stdout, stderr) = proc.communicate()
    rc = proc.returncode
    proc.stdout.close()
    proc.stderr.close()
    return {
        "rc": rc,
        "stdout":stdout,
        "stderr":stderr
    }

def which(exe):
    """Find and return exe in the user unix PATH. It is meant to be the
    equivalent to the UNIX command which.

    Args:
        exe: a string containing the name of the commandline executable to find
             e.g. exe='date'

    Returns:
        A string containing the full path of the first occurrence of exe in the
        user's PATH e.g. '/bin/date'
    """
    path = os.environ.get('PATH', '')
    for directory in path.split(':'):
        if(os.path.exists(os.path.join(directory, exe))):
            return(os.path.join(directory, exe))
    return(None)



def find(directory, pattern, regex=False):
    """
    Find all the files in the directory matching the pattern
    If regex is True, the regular expression pattern matching will be used,
    otherwise the Unix filename pattern matching
    """

    match = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            fabspath = os.path.join(root, f)
            if regex:
                if re.search(pattern, f):
                    match.append(fabspath)
            else:
                if fnmatch.fnmatch(fabspath, pattern):
                    match.append(fabspath)
    return match



def find_one(directory, pattern):
    """
    Find a file matching the pattern and return
    """
    for root, dirs, files in os.walk(directory):
        for f in files:
            fabspath = os.path.join(root, f)
            if fnmatch.fnmatch(fabspath, pattern):
                return fabspath


def format_html(input_file, output_file=None):
    """
    Get an html file as input and create an html output file which contains
    all the resolved link to png and and images
    """

    loadPNGScript = """
    <script type="text/javascript">
    var loadPNG = function(id, path) {
        var xmlhttp;

        if (window.XMLHttpRequest) {
            // code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp = new XMLHttpRequest();
        } else {
            // code for IE6, IE5
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }

        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == XMLHttpRequest.DONE ) {
                if(xmlhttp.status == 200){
                    document.getElementById(id).src = xmlhttp.responseText;
                }
            }
        }

        xmlhttp.open('GET', path, true);
        xmlhttp.send();
    };
    </script>
    """

    #set default output_file
    if not output_file:
        output_file = os.path.join(os.path.dirname(input_file), "fastqc_report_formatted.html")

    bod = re.compile(r'\<body>')
    reg = re.compile(r'''\<img.*(src\s*=\s*["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?).*\>''')
    img_url_prefix = '/api/fs/png?embed=false&path=%s' %  os.path.dirname(input_file)

    count = 0
    with open(input_file, "r") as ifh, open(output_file, "w") as ofh:
        for line in ifh:
            bodymatch = bod.search(line)
            # add the script before the body
            if bodymatch:
                line = loadPNGScript + line

            else:
                imgmatch = reg.search(line)
                # replace images by javascript calls
                if imgmatch:
                    count = count + 1
                    match = imgmatch.group(0)
                    srcattr = imgmatch.group(1)
                    imgpath = os.path.join(img_url_prefix, imgmatch.group(2))
                    line = '%s<script type="text/javascript">%s</script>' % (
                                line,
                                'loadPNG("%s", "%s")' % ('img_%s'%count, imgpath)
                            )
                    line = line.replace(srcattr, 'id="img_%s"'%count)
            ofh.write(line)
    return output_file


def pretty_print(msg):
    """
    Simple logging without logger
    """
    now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    print "%s %s" % (now, msg)


def format_dict(dict,sort_keys=True,indent=None):
    return json.dumps(dict,sort_keys=sort_keys,indent=indent)


def print_dict(dict):
    """
    Pretty print dictionary
    """
    print format_dict(dict,indent=4)


def decode(data):
    """
    For every key of the dictionary replace the _ with a .
    """
    return {k.replace("_", "."):v for k,v in data.items()}


def encode(data):
    """
    For every key of the dictionary replace the _ with a .
    """
    return {k.replace(".", "_"):v for k,v in data.items()}


def dict_update(d1, d2, replace=True):
    """
    Recursively update dictionary d1 with d2.
    If replace is false, only sets undefined keys
    """
    for k, v in d2.iteritems():
        if isinstance(v, collections.Mapping):
            r = dict_update(d1.get(k, {}), v, replace)
            if replace or k not in d1:
                d1[k] = r
        else:
            if replace or k not in d1:
                d1[k] = d2[k]
    return d1

def pretty_number(string):
    """
    Adds commas to numbers to make them more readable, e.g., 10000 becomes 10'000.
    If input string is not a number, does nothing
    """
    result = string
    try:
        float(result)
        # From now on we know we're dealing with a float ;)
        parts = result.split('.')
        new = ''
        for i, s in enumerate(reversed(parts.pop(0))):
            if i>0 and i%3==0:
                new += "'"
            new += s
        result = new[::-1]
        if parts:
            result = "%s.%s" % (result, ''.join(parts))
    except ValueError:
        return result
    return result


def has_write_access(dirname):
    response = False
    dirname.rstrip('/')
    while len(dirname)>1:
        if os.path.isdir(dirname):
            if os.access(dirname, os.W_OK):
                response = True
            break
        else:
            dirname = os.path.split(dirname)[0]
    return response



def utc_tdiff(t2, t1):

    tdiff = t2-t1
    time = {}
    time['d'] = tdiff.days
    time['h'] = tdiff.seconds / 3600  # hours
    time['m'] = (tdiff.seconds / 60) % 60  # minutes
    time['s'] = tdiff.seconds % 60  # seconds
    return time


def format_tdiff(t2, t1):

    tdiff = utc_tdiff(t2, t1)

    str_time = ''
    for key in ['d','h','m','s']:
        if tdiff[key]:
            str_time += '%s%s ' %(tdiff[key], key)
    return str_time


def template_render(template, output_file, **var_list):
    """
    Render a jinja2 template
    """
    loader=jinja2.FileSystemLoader(template)
    env = jinja2.Environment(loader=loader)
    t = env.get_template('')

    with open(output_file, 'w') as fh:
        fh.write(t.render(var_list))
