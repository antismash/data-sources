bytO.hmm: bytO_aligned.faa
	hmmbuild -n bytO bytO.hmm bytO_aligned.faa

bytO_aligned.faa: all_bytO.faa
	mafft --auto all_bytO.faa > bytO_aligned.faa
