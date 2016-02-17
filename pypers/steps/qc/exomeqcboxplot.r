# Script to collect QC metrics for the first DNA plate
#
# Author: Armand Valsesia
#
# See also :
# Picard metrics : https://broadinstitute.github.io/picard/picard-metric-definitions.html
# Qplot metrics : http://genome.sph.umich.edu/wiki/QPLOT#Output_files
#
#
############################################################################


require( plyr )
require( ggplot2 )
require( reshape2 )



args <- commandArgs(trailingOnly = TRUE)
# path to root directory containing the 3 first flow-cells
#DATDIR <- "/nihs/Bioinformatics/genomics_core/Experiments/JINGO/JINGO_NEW/Result/JINGO1/Merge_samples/ExomeMergePipeline_274/ExomeMergePipeline"
HSMETRICS_DIR <- args[1]
QPLOT_DIR <- args[2]

# project directory
#PROJ_DIR <- file.path( Sys.getenv("STUDIES") ,"CT_Tartu/analytical_data/genotyping/exome_seq/" )

#OUT_DIR <- file.path(  "/nihs/Bioinformatics/genomics_core/Experiments/JINGO/JINGO_NEW/Result/JINGO1/Merge_samples/ExomeMergePipeline_274" )
OUT_DIR <- args[3]


dir.create( OUT_DIR , recursive = TRUE , showWarnings = TRUE )

# overwrite ?
OVERWRITE <- FALSE

#'=========================================================================================================
#'====    Helper functions
#'=========================================================================================================


#' Boxplot with stripchart
#' @param dat data.frame
#' @param x.name name of x axis column
#' @param y.name name of y axis column
#' @param group.name name for colour group, leave NULL if none
#' @param ylab name to put on graph for ylabel
#' @param add.ranksum boolean : add ranksum test's pvalue in the plot?
#' @return ggplot2 object
#'
#' @author Armand Valsesia
#' @export
gboxplot <- function( dat , x.name , y.name, group.name = NULL , ylab = y.name ,  add.ranksum = TRUE  ){

  df <- dat[ , c( x.name , y.name , group.name ) ]

  if( !is.null(  group.name ) ){
    # boxplot colored by group.name
    colnames( df ) <- c("x","y","col")
    plt <- ggplot( df, aes( x = x, y = y, color  = col))

  }else{
    # boxplot w/o colors
    colnames( df ) <- c("x","y")
    plt <- ggplot( df, aes( x = x, y = y ))
  }

  # add boxplot (w/o plotting outliers) and add jittered points
  plt <- plt + geom_boxplot( outlier.size = 0) + geom_jitter(  position = position_jitter(width = 0.2, height = 0)  )

  # set x/y labels and remove legends
  plt <- plt + xlab( "" ) + ylab( ylab ) + theme(legend.position = "none")

  # compute ranksum test ?
  df$x <- as.factor( df$x )
  if( nlevels( df$x) == 1 ){
    add.ranksum <- FALSE
  }
  if ( add.ranksum ){


    pv <- formatC( kruskal.test(y ~ x, data  = df )$p.value, digits = 4, format = "f")
    pv.sign <- "="
    if( as.numeric(pv) == 0 ){
      pv <- "1e-4"
      pv.sign <- "<"
    }
    pv <- paste("Ranksum p-value",pv.sign, pv )
    ymin <- min( df$y, na.rm = TRUE ) - diff( range( df$y, na.rm = TRUE ) ) / 10
    plt <- plt + annotate("text", x = 1.8, y = ymin , label = pv, alpha = 0.5  )
  }

  plt
}


#' Make boxplot for a given QC metric
#' @param metric data.frame (with 1 row) and 2 columns: nameOfMetric, descriptionOfMetric
#' @param dat input data.frame
#' @param grp grouping variable
#' @return
#'
#' @author Armand Valsesia
#' @export
wrapPlots <- function( metric, dat , grp = "sampleType" ){
  cat( metric[, 1] , "\n")
  df <- melt( dat[ , c( grp , metric[, 1])])
  plt <-  gboxplot( df , x.name = grp, y.name = "value" , group.name = grp  )
  plt <- plt + ylab( metric[, 1] ) + ggtitle( metric[, 2] ) +  theme(plot.title = element_text( size = 10 ))
  plt

}

#'=========================================================================================================
#'====    Process HsMetrics metrics
#'=========================================================================================================


outfile <- file.path( OUT_DIR , "HsMetric.csv" )

if ( file.exists( outfile ) & !OVERWRITE ){
  hsMetrics <- read.csv( outfile )
}else{


  #' find Picard HsMetrics files
  system.time(
      hsMetricsFiles <- list.files( path  = HSMETRICS_DIR  , pattern = "HsMetric.txt", full.names = TRUE , recursive = TRUE )
  )
  print(hsMetricsFiles)
  #user  system elapsed
  #0.006   0.013   3.812
  length( hsMetricsFiles )
  # [1] 96

  #' read data
  hsMetrics <- ldply( hsMetricsFiles, function( fn ){
        read.table( fn , header = TRUE, sep = "\t" )
      })
  stopifnot( nrow( hsMetrics  ) == length( hsMetricsFiles ) )
  hsMetrics$file <- hsMetricsFiles

  hsMetrics$sampleType <- "study sample"
  hsMetrics$sampleType[ grepl( "hapmap", hsMetrics[, 1], ignore.case = TRUE  ) ] <- "hapmap"

  write.csv( hsMetrics , file = outfile, row.names = FALSE )
}

#' setup metric to plot
metrics <- rbind(
    cbind( "TOTAL_READS", "The total number of reads in the SAM or BAM file examine." ),
    cbind( "PCT_PF_UQ_READS", "PF Unique Reads / Total Reads."),
    cbind( "PCT_PF_UQ_READS_ALIGNED", "PF Reads Aligned / PF Reads."),
    cbind( "PCT_SELECTED_BASES",  "On+Near Bait Bases / PF Bases Aligned."),
    cbind( "MEAN_BAIT_COVERAGE",  "The mean coverage of all baits in the experiment."),
    cbind( "MEAN_TARGET_COVERAGE",  "The mean coverage of targets that received at least coverage depth = 2 at one base."),
    cbind( "PCT_USABLE_BASES_ON_TARGET",  "The number of aligned, de-duped, on-target bases out of the PF bases available."),
    cbind( "FOLD_ENRICHMENT", "The fold by which the baited region has been amplified above genomic background."),
    cbind( "PCT_TARGET_BASES_2X", "The percentage of ALL target bases achieving 2X or greater coverage."),
    cbind( "PCT_TARGET_BASES_20X",  "The percentage of ALL target bases achieving 20X or greater coverage."),
    cbind( "PCT_TARGET_BASES_30X",  "The percentage of ALL target bases achieving 30X or greater coverage."),
    cbind( "PCT_TARGET_BASES_40X",  "The percentage of ALL target bases achieving 40X or greater coverage."),
    cbind( "PCT_TARGET_BASES_50X",  "The percentage of ALL target bases achieving 50X or greater coverage."),
    cbind( "PCT_TARGET_BASES_100X", "The percentage of ALL target bases achieving 100X or greater coverage.")

)
metrics <- as.data.frame( metrics , stringsAsFactors = FALSE  )
colnames( metrics ) <- c("metric", "desc")

#' plot metrics


plts <- dlply( metrics , "metric", wrapPlots, dat = hsMetrics )

pdf( file.path( OUT_DIR , "HsMetrics.pdf" ) )
lapply( plts, show )
dev.off()




#'=========================================================================================================
#'====    Process qplot files
#'=========================================================================================================

outfile <- file.path( OUT_DIR , "qplot.csv" )

if ( file.exists( outfile ) & !OVERWRITE ){
  qplot <- read.csv( outfile )
}else{

  #' find qplotQC.stats files
  system.time(
      qplotFiles <- list.files( path  = QPLOT_DIR  , pattern = "qplotQC.stats", full.names = TRUE , recursive = TRUE )
  )
  #    user  system elapsed
  #   0.006   0.031   0.793

  length( qplotFiles )
  # [1] 96

  #' read data
  qplot <- ldply( qplotFiles, function( fn ){
        df <- read.table( fn , header = FALSE, stringsAsFactors = FALSE , check.names = FALSE, skip = 1 )
        df$file <- fn
        df
      })
  stopifnot( length( unique( qplot[,3] )  ) == length( qplotFiles ) )

  colnames( qplot ) <- c("metric","value","file")
  qplot$flowcell <- gsub( "/.*","" , gsub("^/","",  gsub( QPLOT_DIR, "" , qplot$file ) ))
  qplot$sample <- gsub( "_._.*", "", gsub( ".*/","" ,  qplot$file ) )

  qplot$sampleType <- "study sample"
  qplot$sampleType[ grepl( "hapmap", qplot$sample, ignore.case = TRUE  ) ] <- "hapmap"

  write.csv( qplot , file = outfile, row.names = FALSE )
}

# count nb of times each sample was multiplexed
tmp <- subset( qplot, metric == qplot$metric[1] )
length( unique( tmp$sample )  )
# [1] 96


#' setup metric to plot
metrics <- data.frame(
    metric = c(
        "TotalReads(e6)", "MappingRate(%)", "MapRate_MQpass(%)",
        "TargetMapping(%)", "ZeroMapQual(%)", "MapQual<10(%)",
        "MappedBases(e9)",
        "Q20Bases(e9)", "Q20BasesPct(%)", "MeanDepth", "GenomeCover(%)",
        "EPS_MSE", "EPS_Cycle_Mean", "GCBiasMSE", "ISize_mode"
    ) , stringsAsFactors = FALSE)
metrics$desc <- metrics$metric

qplot2 <- dcast( qplot , file ~  metric, value.var = "value")
qplot2 <- merge(qplot2 , unique( qplot[ , c("file", "sampleType")] ), by = "file", all.x = TRUE, all.y = FALSE )


#' plot metrics

plts <- dlply( metrics , "metric", wrapPlots, dat = qplot2 )

pdf( file.path( OUT_DIR , "qplot.pdf" ) )
lapply( plts, show )
dev.off()


