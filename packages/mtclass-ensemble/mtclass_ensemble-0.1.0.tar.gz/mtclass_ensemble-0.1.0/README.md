# MTClass
Using machine learning to classify eGene-eQTL pairs based on multiple phenotypes. A new framework to conduct multivariate genome-wide association.

## Classification of gene-SNP pairs
We adopted an ensemble machine learning framework to classify an individual's genotype 
based on the vector of expression levels from multiple phenotypes (tissues, exons, isoforms, 
cell types, etc.). In doing so, we hope to uncover eQTLs that have broad effects on gene 
expression across multiple phenotypes.

The main MTClass function in this package is `run_mtclass()` in the `ensemble` module. 
This function accepts the following arguments:

* `expression_df`: gene expression file (see formatting below)
* `genotype_df`: genotypes file (see formatting below)
* `iterations`: number of times to run MTClass, each time with a different random seed.
* `num_cores`: number of multiprocessing cores to use to run the script in parallel.

### Gene expression file
The gene expression file must be structured in the following way, with the first two columns 
being `gene` and `donor`. The rest of the columns are the feature names (phenotypes).
An example is below:

| gene | donor | pheno1 | pheno2 | pheno3 | ... |
| --- | --- | --- | --- | --- | --- |
| HBB | Sample1 | 8.19 | 7.12 | 11.47 | ... |
| HBB | Sample2 | 5.01 | 12.70 | 2.15 | ... |

### Genotypes file
The genotypes file must be structured in the following way, with the first two columns 
being `gene_name` and `ID`. The rest of the columns are the sample names. At least some
of the sample names should match the `donor` column in the gene expression data. The script
will automatically only use the samples that are present in both `genotype_df` and `expression_df`.

**Note**: The formatting of this genotype file is very similar to that of a typical VCF, 
except with the addition of the `gene_name` column and the binarization of the genotypes. An example is below:

| gene_name | ID | Sample1 | Sample2 | ... |
| --- | --- | --- | --- | --- |
| HBB | chr11_12581527_A_T_b38 | 0 | 1 | ... |
| HBB | chr11_12592567_G_C_b38 | 1 | 0 | ... |

### Example usage
We provide an example of using the MTClass classification script with GTEx 
(https://gtexportal.org) expression levels of two genes from 9 tissues. 
To preserve subject confidentiality, the true genotypes of the GTEx donors were 
encoded as 0 or 1. This can be run using the `test_mtclass()` function in 
the `ensemble` module. No arguments are necessary for this function.

## Extracting cis-eQTL genotypes
The MTClass algorithm uses a dominant genetic model to encode the genotypes. Homozygous wild-type is encoded as "0" and heterozygotes/homozygous mutants are encoded as "1". This is done mostly to alleviate class imbalance.

The `extract_eqtl_genotypes()` function uses PLINK2 (https://www.cog-genomics.org/plink/2.0/) to extract and encode genotypes. It assumes that the genotype file is in PLINK2 format (.pgen, .psam, and .pvar files are present).

This function takes in several required arguments:
- `gene_list`: a list of genes. The script will import the GTEx metadata from GENCODE v26 to get the hg38 genomic coordinates for the genes.
- `pfile_path`: path to the PLINK2 .pgen, .psam, and .pvar files (no file extension). By default, the script will look for `genotypes.pgen/.psam/.pvar` in the current working directory.
- `window`: cis window to extract eQTLs. The default is 10,000 base pairs
- `genotype_format`: "binary" (0,1 under a dominant model) or "additive" (0,1,2). The default is "binary".
- `plink_cmd`: the path to the PLINK2 command. The default is simply `plink2`.

## GWAS variant colocalization analysis
One metric for assessing the functionality of our top SNPs is by calculating the colocalization with known GWAS signals. We did this by downloading the entire GWAS Catalog (https://www.ebi.ac.uk/gwas/docs/file-downloads) and searching 10kb upstream and downstream of a given eQTL for known trait associations. We compared our machine learning framework to state-of-the-art linear multivariate approaches, namely MultiPhen and MANOVA, which both output a nominal p-value.

The `gwas_hits()` function within the `gwas_variant_colocalization` module takes in several arguments and outputs a weighted count of the number of GWAS-significant variants within a specified neighborhood. The inputs to the function are:

- `results`: MTClass results dataframe. Can be obtained by running `run_mtclass()`.
- `gwas_table`: GWAS Catalog dataframe. Can be obtained by running `load_gwas_catalog()`.
- `metric`: metric to sort by. If `pval` is contained in the metric, the algorithm will sort in ascending order. Otherwise, it will assume the metric is a classification metric and sort in descending order. 
- `n_top`: number of top eQTLs to include in the analysis.
- `bp`: +/- base pairs to consider in interval. Default=`10_000`.
- `genome`: version that variants are formatted in, according to GTEx. Default=`hg38`. For example, the same variant on chr19:132415 with a REF allele of A and ALT allele of T would be formatted like this in GTEx:

    - `hg19`: 19_132415_A_T_b37
    - `hg38`: chr19_132415_A_T_b38