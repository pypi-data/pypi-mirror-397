"""Testing the module with the python internal unittest module."""

import unittest

from addimportdir import importdir,removedir
# Import Monogram class of pyngramroh module.
from src.pyngramroh import NGram

importdir()

class TestPyngramrohNGram(unittest.TestCase):
    """Test Monogram class of pyngramroh module."""
    
    def setUp(self) -> None:
        self.testlist = ["This is a demo string"]
        self.reslist_words1 = ["This","is","a","demo","string"]
        self.reslist_words2 = ["This_is","is_a","a_demo","demo_string"]
        self.reslist_words3 = ["This_is_a","is_a_demo","a_demo_string"]
        # Chunksize = 2
        self.reslistn1 = ["_T","Th","hi","is","s_","_i","is","s_","_a","a_","_d","de","em","mo","o_","_s","st","tr","ri","in","ng","g_"]
        self.reslistn2 = ["_Th","Thi","his","is_","s_i","_is","is_","s_a","_a_","a_d","_de","dem","emo","mo_","o_s","_st","str","tri","rin","ing","ng_","g_"]

    # Test monogram creation.
    def test_pyngramroh_monogram(self):
        monog = NGram(self.testlist[0])
        self.assertEqual(monog.generate_ngram(), self.reslist_words1)

    # Test bigram creation.
    def test_pyngramroh_bigram(self):
        big = NGram(self.testlist[0],2)
        self.assertEqual(big.generate_ngram(), self.reslist_words2)

        big = NGram(self.testlist[0],2,True)
        self.assertEqual(big.generate_ngram(), self.reslistn1)

    # Test trigram creation.
    def test_pyngramroh_trigram(self):
        trig = NGram(self.testlist[0],3)
        self.assertEqual(trig.generate_ngram(), self.reslist_words3)

        trig = NGram(self.testlist[0],3,True)
        self.assertEqual(trig.generate_ngram(), self.reslistn2)

if __name__ =="__main__":
    # Verbose unittests.
    unittest.main(verbosity=2)
    removedir()