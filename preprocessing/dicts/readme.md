Credits

Below three files come from https://github.com/hackerb9/gwordlist
`count_1w.txt` contains 330K words with freq
`words_alpha.txt` contains 370K words
`frequency-alpha-alldicts.txt` contains 240K words with freq

`prefix_list.csv` parse from https://lhncbc.nlm.nih.gov/LSG/Projects/lvg/current/docs/designDoc/UDF/derivations/prefixList.html
`suffix_list.csv` parse from https://lhncbc.nlm.nih.gov/LSG/Projects/lvg/current/docs/designDoc/UDF/derivations/suffixList.html

I have compared three syllabification methods based on [nltk](https://github.com/nltk/nltk/tree/develop/nltk/tokenize) as well as [syllabify](https://github.com/cainesap/syllabify)

However in the final implementation, **none** of the above syllabfication method is used, the encoding is based on `cmu.dict.txt`.

`cmu.dict.txt` is the [CMU dictionary](https://github.com/cmusphinx/cmudict), an open pronouncing dictionary of American English.

[P2TK](https://sourceforge.net/projects/p2tk/) is another syllabification toolkit but I don't use here.

`wordnet_stopwords.txt` word list that wordnet excludes of function words without actual meaning.
