# StrR-like regulator
===================================================

This model is designed to identify StrR-like pathway specfic regulators (PSR).
StrR-like regulators are known to regulate several important natural product classes that are used clinically, including:
- Glycopeptides (vancomycin, teicoplanin, balhimycin)
- Aminoglycosides (streptomycin, kanamycin)
- Aminocyclitols (spectinomycin)
- Chloramphenicol

### Cutoff
In a leave-one-out analysis, the scores varied from 467.7 (decaplanin) to 312.8 (pyrazofurin)

A quick summary of results against MIBiG 3.1:
- 469.6 (vancomycin) to 318.9 (keratinimicin A) - 59 hits
- 208.5 (streptonigrin) and 198.1 (cremeomycin) 
- 16.6 (aldgamycin) to -12.9 (xenovulene A) - 29 hits

Base on this, a cutoff of 150 is used, which would identify putative regulators
in cremeomycin (198.1) and streptonigrin (208.5) which were the lowest scoring real hits from MiBIG.

### Data Source
This hmmmodel was created from a list of 83 validated sequences identified in this paper:
The Impact of Heterologous Regulatory Genes from Lipodepsipeptide Biosynthetic Gene Clusters on the Production of Teicoplanin and A40926
https://www.mdpi.com/2079-6382/13/2/115

### Code and Sequence availbility
All sequences, the model and model validation scripts can be found here: 
https://github.com/Sam-Will/StrR_regulator_hmm
