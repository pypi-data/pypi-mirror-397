"""
Pyngramroh

A cross plattform ngram module.

Usage:
    from pyngramroh import *
    ng = NGram("Demo",2,True)
    ng.create_ngram()
    
Returns:
    ['_D', 'De', 'em', 'mo', 'o_']

Author: IT-Administrators

License: MIT
"""
# Functions an classes that can be imported by calling from <modulename> import *
from .ngram import NGram