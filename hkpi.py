#!/usr/bin/python3.8
import readline
import os
import sys
from pykeepass import PyKeePass
import ctypes
import re
import jmespath

class cmds_desc:
  
  def __init__(self):
    self.cmds={
      "cd": {
        "opts": "",
        "match_types": ["d"],
        "aliase": []
      }
    }

  def __del__(self):
    pass


class hkpi_general(cmds_desc):

  def __init__(self):
    super().__init__()
    self.kpdb=None
    self.pwd="/a/b/c/d/e/f/g"
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

  def resolve_path(self, path):
    if not path: return self.pwd
    else:
      path_new=self.pwd
      path_spl=[x for x in re.split("/+", path) if x]
      #print(f"path_spl: {path_spl}")
      pwd_spl=[x for x in re.split("/+", self.pwd) if x]
      if path.startswith("/"):
        path_new_spl=[]
      else:
        path_new_spl=pwd_spl
      c=1
      for d in path_spl:
        if (not d) or re.match("^\.{1}$",d): 
          continue
        elif re.match("^\.{2,}$",d):
          _o=len(path_new_spl)-(c)
          path_new_spl=path_new_spl[0:_o]
          c+=1
        else:
          path_new_spl.append(d)
          c=1
        #print(f"3 c: {c} d: {d} path_new: {path_new_spl}")
      if len(path_new_spl)==0: 
        return "/"
      else:
        return "/"+"/".join(path_new_spl)

  def list_dir(self, path):
    pass
    
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
      else:
        print(self.resolve_path(i))

a=hkpi()
a.run() 
