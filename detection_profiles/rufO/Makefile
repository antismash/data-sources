rufO.hmm: rufO_aligned.faa
	hmmbuild -n rufO rufO.hmm rufO_aligned.faa

rufO_aligned.faa: rufO.faa
	mafft --auto rufO.faa > rufO_aligned.faa

ruf0.faa: ruf0.tsv
	./fetch.sh
