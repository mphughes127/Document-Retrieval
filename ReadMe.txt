To run program extract files then navigate to folder containing python files in a console and run DocumentRetrieval.py

to view help command would be 'python DocumentRetrieval.py -h' this allows user to see which command line
options are mandatory. The help is given below

USE: python DocumentRetrieval.py (options) keyfile response
ACTION: computes IR system performance measures, given input files:

    OPTIONS:
        -h : print this help message
        -s FILE : use stoplist file FILE (not Required)
        -d FILE : use document Collection file FILE (required if not reading index file)
        -q FILE : use query file FILE (required)
        -S Boolean : use stemming (not required)
        -i FILE : index file for either reading or creating based on I option FILE (required)
        -I Boolean : create index file (if not included read index file i)
        -m : method of term weighting can be 'b' (binary), 'tf' (term frequency) or 'tfidf' (term frequency, inverse document frequency) (required)
        -n Int : number of documents to return per query (required)
        -r FILE : create results file FILE (required)


an example command to run the program with all options is:

python DocumentRetrieval.py -d documents.txt -q queries.txt -i index.txt -I -s stop_list.txt -S -m tfidf -n 10 -r results.txt

This would run the program on collection documents.txt with queries queries.txt, stoplist stop_list.txt, Stemming activates,
TF.IDf term weighting, 10 documents retrieved per query and the result being stored in results.txt. An index file would also be
created on this run.

for alternative behaviour non mandatory options can be removed or -m can be changed