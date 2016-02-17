use strict;
use Getopt::Long::Descriptive;
use Bio::KBase::GenomeAnnotation::GenomeAnnotationImpl;
#use Bio::KBase::GenomeAnnotation::Client;
use JSON;
use File::Slurp;
use Data::Dumper;

=head1 DESCRIPTION

Generic script to call kbase Genome Annotation Service subroutines

A perl script to call individual annotation subroutines in the kbase Genome Annotation Service

Instantiates a modified GenomeAnnotation Client Implementation (NOT the Client)

Converts the input genome (a kbase 'genomeTO' object) json file to a perl hash. 
Calls the subroutine with any appropriate params and writes the output genome to file.

=cut

my ($opt, $usage) = describe_options(
    'call_kbase_annotation',
    [ 'genome|g=s', "the input genome", { required => 1  } ],
    [ 'subroutine|s=s', "the annotation subroutine to run, eg call_features_tRNA_trnascan", { required => 1  } ],
    [ 'output|o=s', "the output filename", { required => 1  } ],
    [ 'params|p=s', "params to evaluate as a perl hash or array, eg \"{'spam'=>'eggs'}\", required by subroutine as second argument."],
    [ 'help',       "print usage message and exit" ],
  );

print($usage->text), exit if $opt->help;

my $genome_fn = $opt->genome;
my $sub_routine = $opt->subroutine;
print "Runnning $sub_routine for  $genome_fn\n";

my $params;
if ($opt->params) {
    $params = eval($opt->params);
}

# parse genome into perl hash
my $json = JSON->new->allow_nonref;
my $json_txt = read_file($genome_fn);
my  $json_data = $json->decode($json_txt);

# GenomeAnnotationImpl is a modified copy of the standard kbase install
my $client = Bio::KBase::GenomeAnnotation::GenomeAnnotationImpl->new();
my $genome_out;
if ($opt->params) {
    $genome_out = $client->$sub_routine($json_data,$params);
}
else {
    $genome_out = $client->$sub_routine($json_data);
}

# print output genome to file
$json = $json->indent();
$json_txt =  $json->encode($genome_out);

open my $fh, ">", $opt->output;
print $fh $json_txt;
close $fh;
