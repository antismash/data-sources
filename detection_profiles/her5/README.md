The sequence alignment for the creation of a profile for the detection of **herbicidin** BGCs (specifically, the proteins required for the **aureonuclemycin** scaffold, see: https://pubs.acs.org/doi/10.1021/jacs.2c05728).

To create the aligment, I identified conserved clusters of the 4 core genes (Her4-7) in the NCBI database (w/c 28/07/2025) using cblaster. Cases where hits were duplicated were omitted and the remaining single copy orthologous were used to make the models.

The bitscores were estimated based on the distribution of hit using the online HMMsearch versus the [reference proteome database at EBI](https://www.ebi.ac.uk/Tools/hmmer/search/hmmsearch). These bitscores are relatively high compared to other rules, but identified herbicidins and several variants.

