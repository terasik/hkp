#!/usr/bin/python3.8
import readline
import os
import sys
from pykeepass import PyKeePass
import ctypes
import re

class hkpi_general:

  def __init__(self):
    self.kpdb=None
    self.poss_match=["tut", "i" , "ne", "daleko", "kak" , "wesna"]
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(" \n\t=")
    readline.set_completer(self.completer)
    libreadline = ctypes.CDLL (readline.__file__)
    rl_completer_quote_characters = ctypes.c_char_p.in_dll (
        libreadline, 
        "rl_completer_quote_characters"
    )
    rl_completer_quote_characters.value = b"\"'"
    
  def open_kpdb(self, kpdb=sys.argv[1]):
    self.kpdb=PyKeePass(kpdb, "abc")

  def get_cur_before(self):
    idx = readline.get_begidx()
    full = readline.get_line_buffer()
    r=full[:idx]
    return r

  def completer(self, text, state):
    pref = self.get_cur_before()
    n = pref.split()
    #cmd = n[0] if len(n) > 0 else ""
    if text == "":
      matches = self.poss_match
    else:
      matches = [x for x in self.poss_match if x.startswith(text)]
    # return current completion match
    if state > len(matches):
     return None
    else:
     return matches[state]


class hkpi(hkpi_general):
  def __init__(self):
    super().__init__()
    self.open_kpdb()
    print(self.kpdb.entries)
  def run(self):
    while True:
      prompt="> "
      i=input(prompt).strip()
      #i=self.input_with_prefill(prompt, self._gen_str())
      if re.match("^(exit|break|quit)$", i): sys.exit(0)

a=hkpi()
a.run() 
