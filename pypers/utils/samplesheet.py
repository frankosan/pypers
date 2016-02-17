import csv
import os
import shutil
import pandas as pd


class SampleSheet(object):
    """
    Utility class extract information from a sample sheet
    """
    # Headers:
    # - Hiseq: FCID, Lane, SampleID, SampleRef, Index, Description, Control, Recipe, Operator, SampleProject 
    # - Miseq:      Sample_ID, Sample_Name, Sample_Plate, Sample_Well, index, Sample_Project, Description
    # - Miseq dual: Sample_ID, Sample_Name, Sample_Plate, Sample_Well, index, index2, Sample_Project, Description

    file_name = ""
    data = pd.DataFrame()

    def __init__(self, file_name):
        """
        Fill the information
        """
        self.file_name = file_name
        with open(self.file_name) as fh:
            header = fh.readline()
            while not (header.startswith('FCID') or header.startswith('Sample_ID')):
                header = fh.readline()
            header = header.rstrip()
            header = header.split(',')
            self.data = pd.read_csv(fh, names=header, comment='#').dropna(how='all')
            # Sanitize the data...
            self.data.replace("nnnnn", "", inplace=True)
            self.data.replace("[\"\'?\(\)\[\]\/\\\=\+\<\>\:\;\,\*\^\|\&\.]", "", inplace=True, regex=True)
            self.data.replace(' ', '_', inplace=True)

    def get_project_name(self):
        """
        Return the project name (only one value allowed)
        """
        project_names = set(self.data.filter(regex='Sample.*Project').iloc[:,0])
        if len(project_names)>1:
            raise Exception("More than one project name found: %s" 
                             % ','.join([str(s) for s in project_names]))
        return project_names.pop()


    def get_sample_ids(self):
        """
        Return a list of unique sample ids
        """
        return set(self.data.filter(regex='Sample.*ID').iloc[:,0])


    def get_lanes(self):
        """
        Return a list of unique lane ids
        """
        lanes = set()    
        if 'Lane' in self.data.columns:
            lanes = set(self.data['Lane'].astype(str))
        return lanes


    def get_lines_count(self):
        """
        Number of lines in sample sheet
        """
        return self.data.shape[0]


    def get_mask_length(self):
        """
        Return the length of the mask from a sample sheet
        """
        mask_length = 0
        double_idx  = False

        if 'Index' in self.data.columns: # Hiseq
            # Get mask from first index
            index = self.data.ix[0, 'Index']
            mask_length = len(index.split("-")[0])
            if "-" in index:
                    double_idx = True
        elif 'index' in self.data.columns: # Miseq
            if 'index2' in self.data.columns:
                double_idx = True
            index = self.data.ix[0, 'index']
            mask_length = len(index)

        return (mask_length, double_idx)


    def get_val(self, column):
        """
        Return the first value of the given column of 'n/a' if column does not exist.
        Useful to get the value of a constant column.
        """
        val = 'n/a'
        if column in self.data.columns:
            val = self.data.loc[0, column]
        return val


    def create_map(self):
        """
        Return map file as a list of lines
        """
        file_lines = [['#SampleID', 'BarcodeSequence', 'LinkerPrimerSequence', 'Description']]
        if 'index' in self.data.columns:
            df = self.data.ix[:,['Sample_ID', 'Sample_Project']]
            df['BarcodeSequence'] = self.data['index']
            if 'index2' in self.data.columns:
                df['BarcodeSequence'] += self.data['index2']
            df['LinkerPrimerSequence'] = ''
            df = df.rename(columns={'Sample_ID':'#SampleID', 'Sample_Project':'Description'})
            file_lines.extend(df[file_lines[0]].values.tolist())

        return file_lines


    @staticmethod
    def get_map_barcode_length(map):
        """
        return the length of the barcode in the map file
        """
        map_csv = csv.reader(open(map), delimiter='\t')
        barcode_list = list(set(columns[1] for columns in map_csv))

        return len(barcode_list[0])


    @staticmethod
    def compare_map_files(map_a, map_b):
        """
        compares the SampleID and the BarcodeSequence columns
        of both files
        """

        map_a_csv = csv.reader(open(map_a), delimiter='\t')
        map_b_csv = csv.reader(open(map_b), delimiter='\t')

        sample_ids_a = list(set(columns[0] for columns in map_a_csv))
        sample_ids_b = list(set(columns[0] for columns in map_b_csv))

        if sample_ids_a != sample_ids_b:
            return False

        barcodes_a = list(set(columns[1] for columns in map_a_csv))
        barcodes_b = list(set(columns[1] for columns in map_b_csv))

        if barcodes_a != barcodes_b:
            return False

        return True



    def validate(self, project_name, sample_sheet_validated):
        """
        Create a validated sample sheet and return the path to it
        Args:

        - project_name: the project name
        - sample_sheet_validated: the path to the output file.
        """
        casava_fields = ['FCID', 'Lane', 'SampleID', 'SampleRef', 'Index', 
                'Description', 'Control', 'Recipe', 'Operator', 'SampleProject' ]
        if 'FCID' in self.data.columns:
            df = self.data[casava_fields]
            df['SampleProject'] = project_name
            with open(sample_sheet_validated, "w") as ss_validated:
                ss_validated.write(self.data.to_csv(index=False))
        else:
            raise Exception("Can only validate sample sheet for Hiseq")
        return sample_sheet_validated
