""" 
 This file is part of Pypers.

 Pypers is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Pypers is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Pypers.  If not, see <http://www.gnu.org/licenses/>.
 """

import os
import re
import csv
from pypers.utils.samplesheet import SampleSheet

class Fofn(object):
    """
    Utility class utilised to create and validate file of file names (Fofn)
    """
    r1_regex = re.compile("(.*)_(r1)_(.*)", re.I)
    r2_regex = re.compile("(.*)_(r2)_(.*)", re.I)

    @staticmethod
    def _write_record(output_file, r1_file, r2_file, sample_id):
        print (r1_file, r2_file, sample_id)
        output_file.write("%s,%s,%s\n" % (r1_file, r2_file, sample_id))



    @staticmethod
    def validate(file_name):
        """
        Parse the input fofn file and return a list of error messages
        """

        error_msgs = []

        if not os.path.isfile(file_name):
            error_msgs.append(
                'invalid `list_file`: file %s does not exists'
                % file_name
            )
        else:
            #constants
            fq1_column = 0
            fq2_column = 1
            sampleid_column = 2

            badlines = []

            #check list_file is well formatted
            with open(str(file_name), 'r') as f_fofn:
                lineno = 0
                #the fofn must have 3 columns: fq1, fq2, sample_id
                fq1_exists = False
                fq1_missing = False
                fq2_exists = False
                fq2_missing = False
                for line in csv.reader(f_fofn):
                    lineno += 1

                    if line[fq1_column].startswith("#"):
                        pass # <---skip the comments
                    else:

                        if len(line) != 3:
                            #######################################
                            # Check if the file contatins 3 columns
                            #######################################
                            badlines.append(
                                "line %s : 3 column required, only %s column found"
                                %(lineno, len(line))
                            )
                        else:
                            #######################################
                            # Check each column
                            #######################################
                            if line[fq1_column]:
                                fq1_file = line[fq1_column].strip()
                                fq1_exists = True
                                if not os.path.exists(fq1_file):
                                    badlines.append(
                                        "line %s column %d: file does not exists"
                                        %(lineno, fq1_column + 1)
                                    )
                                if not re.search("(.*)(_r1_|\.r1\.|_r1\.)(.*)", os.path.basename(fq1_file), re.I):
                                    badlines.append(
                                        "line %s column %d: file name does not contain _R1_ or _r1. or .r1."
                                        %(lineno, fq1_column + 1)
                                    )
                            else:
                                fq1_missing = True

                            if line[fq2_column]:
                                fq2_file = line[fq2_column].strip()
                                fq2_exists = True
                                if not os.path.exists(fq2_file):
                                    badlines.append(
                                        "line %s column %d: file does not exists"
                                        %(lineno, fq2_column + 1)
                                    )
                                if not re.search("(.*)(_r2_|\.r2\.|_r2\.)(.*)", os.path.basename(fq2_file), re.I):
                                    badlines.append(
                                        "line %s column %d: file name does not contain _R2_"
                                        %(lineno, fq2_column + 1)
                                    )

                            else:
                                fq2_missing = True


                            sample_id = line[sampleid_column].strip()
                            if not sample_id:
                                badlines.append(
                                    "line %s column %d: sample ID missing"
                                    %(lineno, sampleid_column)
                                )

                if fq1_exists and fq1_missing:
                    badlines.append(
                        "Inconsistent CSV file on fq1 column"
                    )
                if fq2_exists and fq2_missing:
                    badlines.append(
                        "Inconsistent CSV file on fq2 column"
                    )


            if badlines:
                error_msgs.append('A FoFN `list_file` has to be formatted CSV file with 3 columns where:')
                error_msgs.append(' - column 1 must contains the first read of a sample')
                error_msgs.append(' - column 2 must contains the second read of a sample')
                error_msgs.append(' - column 3 must contains the sample ID')
                error_msgs.append('The following lines in the input FoFN are malformatted:')
                error_msgs += badlines


        return error_msgs


    @staticmethod
    def create(sample_sheet, input_dir, output_dir=None, output_file_name=None):
        """
        Crete a file of file names and return the path to it

        Args:
             sample_sheet:
                full path to the sample sheet

             input_dir:
                path to the directory containing the input files

             output_file:
                name of the output fofn. If is not specified the name
        """


        if not os.path.exists(sample_sheet):
            raise Exception("input error: parameter `sample_sheet` %s does not exist" % sample_sheet)

        if not os.path.exists(input_dir):
            raise Exception("input error: parameter `input_dir` %s does not exist" % sample_sheet)


        print("*********************************")
        print("sample_sheet: %s" % os.path.abspath(sample_sheet))
        print("input_dir: %s" % os.path.abspath(input_dir))
        print("*********************************")

        #set default name of the output fofn
        if not output_file_name:
            output_file_name = os.path.basename(sample_sheet).rsplit(".", 1)[0] + "_fofn.csv"

        if not output_dir:
            output_dir = os.path.dirname(sample_sheet)

        output_file = os.path.join(output_dir, output_file_name)

        with open(output_file, 'w') as f_fofn:
            ss = SampleSheet(sample_sheet)
            sample_id_list = ss.get_sample_ids()
            for sample_id in sample_id_list:
                print("*********************************")
                print "sample_id : %s" %sample_id
                for root, dirs, file_list in os.walk(input_dir):
                    #group the files by sample id and read number
                    r1_files = [
                        os.path.join(root, file_name) for file_name in file_list if (
                            '%s_'%sample_id in file_name and Fofn.r1_regex.search(file_name)
                        )
                    ]
                    r2_files = [
                        os.path.join(root, file_name) for file_name in file_list if (
                            '%s_'%sample_id in file_name and Fofn.r2_regex.search(file_name)
                        )
                    ]

                    r1_file = ""
                    r2_file = ""

                    if r1_files:
                        for r1_file in r1_files:
                            #filter the R2 files that match the R1 file base
                            r2_matchs = [
                                r2_file for r2_file in r2_files if (
                                    Fofn.r1_regex.search(r1_file).group(1) in r2_file)
                            ]
                            if r2_matchs:
                                Fofn._write_record(f_fofn, r1_file, r2_matchs[0], sample_id)
                            else:
                                if r2_files:
                                    print("No R2 found for sample Id %s" % sample_id)
                                Fofn._write_record(f_fofn, r1_file, '', sample_id)
                    else:
                        if r2_files:
                            for r2_file in r2_files:
                                Fofn._write_record(f_fofn, r1_file, r2_file, sample_id)


        return output_file

    @staticmethod
    def get_columns(file_name, row):
        """
        Return a specific row of the csv already splitted in columns
        """
        columns = []
        with open(file_name) as fofn:
            columns = list(fofn)[row].split(",")
            columns = [column.strip() for column in columns]
        return columns

    @staticmethod
    def count_lines(file_name):
        """
        Count all the lines in the file that do not start with a `#`
        """
        total = 0
        with open(file_name, 'r') as f:
            total = sum(1 for line in f.readlines() if line.strip() and not line.startswith('#'))

        return total

    @staticmethod
    def get_file_list(file_name):
        """
        Return all files in a fofn
        """
        ret_list = [columns[0] for columns in csv.reader(open(file_name))]
        ret_list.extend([columns[1] for columns in csv.reader(open(file_name))])
        return ret_list

    @staticmethod
    def get_samples_list(file_name):
        """
        Return a specific row of the csv already splitted in columns
        """
        return list(set(columns[2] for columns in csv.reader(open(file_name)) if not columns[0].startswith('#')))


    @staticmethod
    def get_files_by_sample(file_name, sample_id):
        """
        Get all the files matching the input sample
        """
        return list(set(columns[0] for columns in csv.reader(open(file_name)) if columns[2].startswith(sample_id)))

    @staticmethod
    def get_rows(file_name):
        """
        Return list of all get_columns
        """
        ret_list = []
        with open(file_name) as fh:
            for row in csv.reader(fh):
                clean_row = [r.rstrip().lstrip() for r in row]
                ret_list.append(clean_row)
        return ret_list

if __name__ == '__main__':
    Fofn.create("/pypers/develop/integration_tests/exome_mapping/sample_sheet_validated.csv", 
                "/pypers/develop/integration_tests/exome_mapping",
                "/scratch/rdferrarfr1/testfofn")
