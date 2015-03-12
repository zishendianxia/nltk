# -*- coding: utf-8 -*-
# Natural Language Toolkit: An Crubadan N-grams Reader
#
# Copyright (C) 2001-2015 NLTK Project
# Author: Avital Pekker <avital.pekker@utoronto.ca>
#
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
An NLTK interface for the n-gram statistics gathered from
the corpora for each language using An Crubadan.

There are multiple potential applications for the data but
this reader was created with the goal of using it in the
context of language identification.

For details about An Crubadan, this data, and its potential uses, see:
http://borel.slu.edu/crubadan/index.html
"""

from __future__ import print_function, unicode_literals

import re
from os import path

from nltk.corpus.reader import CorpusReader
from nltk.probability import FreqDist
from nltk.data import ZipFilePathPointer

class CrubadanCorpusReader(CorpusReader):
    """
    A corpus reader used to access language An Crubadan n-gram files.
    """
    
    _LANG_MAPPER_FILE = 'table.txt'
    all_lang_freq = {}
    
    def __init__(self, root, fileids, encoding='utf8', tagset=None):
        super(CrubadanCorpusReader, self).__init__(root, fileids, encoding='utf8')
        self._lang_mapping_data = []
        self._load_lang_mapping_data()
        self._load_all_ngrams()
        
    def lang_freq(self, lang):
        ''' Return n-gram FreqDist for a specific language
            given ISO 639-3 language code '''
        
        if len(self.all_lang_freq) == 0:
            self._load_all_ngrams()

        return self.all_lang_freq[lang]
    
    def langs(self):
        ''' Return a list of supported languages as ISO 639-3 codes '''
        return [row[1] for row in self._lang_mapping_data]
            
    def iso_to_crubadan(self, lang):
        ''' Return internal Crubadan code based on ISO 639-3 code '''
        for i in self._lang_mapping_data:
            if i[1].lower() == lang.lower():
                return unicode(i[0])
    
    def crubadan_to_iso(self, lang):
        ''' Return ISO 639-3 code given internal Crubadan code '''
        for i in self._lang_mapping_data:
            if i[0].lower() == lang.lower():
                return unicode(i[1])
    
    def _load_lang_mapping_data(self):
        ''' Load language mappings between codes and description from table.txt '''
        if isinstance(self.root, ZipFilePathPointer):
            raise RuntimeError("Please install the 'crubadan' corpus first, use nltk.download()")
        
        mapper_file = path.join(self.root, self._LANG_MAPPER_FILE)
        if self._LANG_MAPPER_FILE not in self.fileids():
            raise RuntimeError("Could not find language mapper file: " + mapper_file)
        
        raw = open(mapper_file, 'rU').read().decode('utf-8').strip()
        self._lang_mapping_data = [row.split('\t') for row in raw.split('\n')]
        
    def _load_lang_ngrams(self, lang):
        ''' Load single n-gram language file given the ISO 639-3 language code
            and return its FreqDist '''
        
        crubadan_code = self.iso_to_crubadan(lang)
        ngram_file = path.join(self.root, unicode(crubadan_code) + '-3grams.txt')
        
        if not path.isfile(ngram_file):
            raise Runtime("Could not find language n-gram file for " + lang)

        counts = FreqDist()
            
        f = open(ngram_file, 'rU')
        
        for line in f:
            data = line.decode('utf-8').split(' ')
            
            ngram = data[1].strip('\n')
            freq = int(data[0])
            
            counts[ngram] = freq
            
        return counts

    def _load_all_ngrams(self):
        ''' Create a dictionary of every supported language mapping 
            the ISO 639-3 language code to its corresponding n-gram
            FreqDist. The result can be accessed via "all_lang_freq" var '''
        
        # Filter out non n-gram files from the corpus dir
        valid_files = []
        for f in self.fileids():
            m = re.search('(\w+)' + re.escape("-3grams.txt"), f)
            if m:
                valid_files.append( m.group() )
                
        for f in valid_files:
            ngram_file = path.join(self.root, f)
            
            if path.isfile(ngram_file):
                crubadan_code = f.split('-')[0]
                iso_code = self.crubadan_to_iso(crubadan_code)

                fd = self._load_lang_ngrams(iso_code)
                self.all_lang_freq[iso_code] = fd

