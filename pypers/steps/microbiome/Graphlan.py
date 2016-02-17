from pypers.core.step import Step
import os

class Graphlan(Step):
    spec = {
        "version": "0.01",
        "descr": [
            """
            Runs the GraPhlAn package (bitbucket) to generate a cladogram .png from .rings.txt and tree.txt files
            GraPhlAn is python version dependent
            """
        ],
        "args":
        {
            "inputs": [
                {
                    "name"     : "input_rings",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "The input rings file",
                },
                {
                    "name"     : "input_tree",
                    "type"     : "file",
                    'iterable' : True,
                    "descr"    : "The input tree file",
                }
            ],
            "outputs": [
                {
                    "name"  : "output_png",
                    "type"  : "file",
                    "descr" : "The output png graphic"
                }
            ],
            "params": [
                {
                    "name"  : "graphlan_path",
                    "type"  : "str",
                    "descr" : "The path to the humann installation directory",
                    "value" : '/software/pypers/graphlan/graphlan-0.9.7',
                    "readonly" : True
                },
                {
                    "name"  : "python_path",
                    "type"  : "str",
                    "descr" : "The path to the python installation required by graphlan",
                    "value" : '/software/pypers/python/Anaconda-1.8.0/bin/python',
                    "readonly" : True
                },
                {
                    "name"  : "dpi",
                    "type"  : "int",
                    "descr" : "The DPI value to use for the png",
                    "value" : 100
                },
                {
                    "name"  : "pad",
                    "type"  : "float",
                    "descr" : "The pad value to use for the png",
                    "value" : 1.4
                },
                {
                    "name"  : "size",
                    "type"  : "float",
                    "descr" : "The size of the png",
                    "value" : 4.0
                }
            ]
        },
        "requirements": { 
        },
    }


    def process(self):

        if not os.path.isfile(self.input_rings):
            raise Exception('[Cannot find file %s]' % self.input_rings)
        if not os.path.isfile(self.input_tree):
            raise Exception('[Cannot find file %s]' % self.input_tree)

        fileName, fileExt = os.path.splitext(os.path.basename(self.input_rings))
        output_xml = '%s/%s.xml' % (self.output_dir,fileName)
        self.output_png = '%s/%s.png' % (self.output_dir,fileName)
        
        cmds=[]
        cmds.append('%s %s/graphlan_annotate.py --annot %s %s %s' % (self.python_path, self.graphlan_path, self.input_rings, self.input_tree, output_xml))
        cmds.append('%s %s/graphlan.py --dpi %s --size %s --pad %s %s %s' % (self.python_path,self.graphlan_path,self.dpi,self.size,self.pad,output_xml,self.output_png))

        for cmd in cmds:
            self.submit_cmd(cmd)

        if not os.path.isfile(self.output_png):
            raise Exception('[Failed to create %s]' % self.output_png)
