
Brief description of Python version of LARA
-------------------------------------------

Top-level functionality
-----------------------

(working on many examples)

1. Internalise a LARA file into JSON form. lara_split_and_clean.py

2. Use TreeTagger to tag a LARA file. lara_top.pl, lara_treetagger.py

3. Download metadata for "distributed LARA". lara_download_metadata.py

4. Carry out "resources" part of LARA compilation. lara_top.pl, lara.pl

5. Carry out "word_pages" part of local LARA compilation. lara_top.pl, lara.pl

(left to do)

6. Carry out "distributed LARA" compilation.

Files used 
----------

lara_audio.py
Processing of things that have to do with audio files.

lara_download_metadata.py
Collect all metadata for a given reading progress and put it in a tmp dir
Create a metametadata file to summarise it.

lara_extra_info.py
Add mouseover annotations to words.
Add links to external resources in word pages.

lara_html.py
HTML headers and footers.

lara_images.py
Processing of things that have to do with images.

lara_parse_utils.py
Utilities for parsing LARA strings.

lara_run.pl
Invoke LARA functionality from command-line.

lara_split_and_clean.py
Read a LARA file and convert it into internal form.

lara_tagging.py
Tag a LARA file using Python NLTK
Probably obsolete, since we're now using TreeTagger

lara_top.pl
Top level: read information from a config file and make appropriate calls.

lara_treetagger.py
Tag a LARA file using TreeTagger.

lara_utils.py
Utility functions.

run_lara_download_metadata.py
Top-level file to call lara_download_metadata.py from the command-line

run_lara_tagging.py
Top-level file to call lara_tagging.py from the command-line
Probably obsolete, since we're now using TreeTagger

