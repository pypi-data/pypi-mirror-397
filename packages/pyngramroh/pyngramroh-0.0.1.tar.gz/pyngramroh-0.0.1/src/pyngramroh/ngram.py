"""
Pyngramroh.ngram

Create an ngram of the provided string.
"""

class NGram:
    """NGram class."""

    def __init__(self, source:str, ngramcount:int = 1, ignore_words:bool = False, delimiter:str = " ", blank_replacement = "_"):
        self.source = source
        self.ngramcount = ngramcount
        self.ignore_words = ignore_words
        self.delimiter = delimiter
        self.blank_replacement = blank_replacement

    def generate_ngram(self) -> list[str]:
        """
        Generate ngrams of the specified text using the ngramcount. 
        The ngramcount is the number of words/characters which will be grouped together.
        The result is a list of strings. 

        Usage:
            from pyngramroh import ngram as ng
            ngram = ng.NGram("This is a demo string", 2)
            print(ngram.generate_ngram())

        Returns:
            ['This_is', 'is_a', 'a_demo', 'demo_string']

        Author: IT-Administrators

        License: MIT
        """
        if self.ignore_words == True:
            
            newstr = self.blank_replacement + self.source.replace(self.delimiter,self.blank_replacement) + self.blank_replacement
            resl = []
            for i in range(len(newstr)):
                resl.append(newstr[:self.ngramcount])
                newstr = newstr[1:]

            resl.pop()
            return resl


        else:
            self.words = self.source.split(self.delimiter)

            # Result should be [[list1],[list2],[list3]]
            # Result list.
            ngramr = []
            # Sublists.
            ngramg = []
            counter = 0

            while counter < len(self.words):
                # Append word to sublist.
                ngramg.append(self.words[counter])
                if len(ngramg) == self.ngramcount:
                    # Append sublist to result list.
                    ngramr.append(self.blank_replacement.join(ngramg))
                    # Remove first word from sublist.
                    ngramg = ngramg[1:]
                counter += 1

            return ngramr