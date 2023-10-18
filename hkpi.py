#!/usr/bin/python3.8
import readline
import os
import sys
from pykeepass import PyKeePass
import ctypes
import re
import jmespath


"""
path=[] name=Database
path=['gr1'] name=gr1
path=['gr1', 'gr2'] name=gr2
path=['gr1', 'gr34'] name=gr34
path=['rg1'] name=rg1
path=['rg1', 'gr with space'] name=gr with space
path=['gr 45'] name=gr 45
path=['rg2'] name=rg2


path=['gr1', 'en1'] name=en1
path=['gr1', 'gr2', 'some entry'] name=some entry
path=['gr1', 'gr2', 'some new .'] name=some new .
path=['rg1', 'in_root'] name=in_root
path=['rg1', 'ohhh tre'] name=ohhh tre
path=['rg1', 'gr with space', 'en_87'] name=en_87
"""


class cmds_desc:
  
  def __init__(self):
    self.cmds={
      "cd": {
        "sopts": [],
        "lopts": [],
        "complete_type": "group",
        "aliase": []
      },
      "ls": {
        "sopts": ["-l", "-t", "-r"],
        "lopts": ["--list", "--time", "--reverse"],
        "complete_type": "group_entry"
      },
      "ec": {
        "sopts": ["-a", "-b", "-c"],
        "lopts": ["--pizdez", "--suka", "--bljadj"],
        "complete_type": "entry"
      }
    }

  def __del__(self):
    pass


class hkpi_general(cmds_desc):

  def __init__(self):
    super().__init__()
    self.kpdb=None
    self.pwd="/"
    self.pwd_for_compl=self.pwd
    self.poss_match_def=list(self.cmds.keys())
    self.poss_match=[]
    self.complete_type_def="cmd"
    self.complete_type=self.complete_type_def
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

  def find_group_by_path(self, path=""):
    if not path: path=self.pwd
    path=[x for x in path.split("/") if x]
    return self.kpdb.find_groups_by_path(path)

  def subdir_names(self, group, end_slash=True):
    e_s=""
    if end_slash: e_s="/"
    return [g.name+e_s for g in group.subgroups]


  def get_group_list(self, arg):
    arg_full=self.resolve_path(arg)
    arg_part=arg_full[len(self.pwd_for_compl):]
    old_group=self.find_group_by_path(self.pwd_for_compl)
    next_gr=self.find_group_by_path(arg_full)
    #print(f"raw path: {path}")
    path=self.resolve_path(path)
    #print(f"res path: {path}")
    path=[p for p in re.split("/+", path) if p]
    #print(f"spl path: {path}")
    path=path[:-1]
    if not path:
      mg=self.kpdb.root_group
    else:
      mg=self.kpdb.find_groups_by_path(path)
    #print(f"main grp: {mg}")
    grs=[]
    if mg:
      for g in mg.subgroups:
        if mg==self.kpdb.root_group:
          grs.append("/"+g.name+"/")
        else:
          grs.append(g.name+"/")
    #print(f"grps: {grs}")
    return grs 

  def set_poss_match(self, arg, cmd):
    m=[]
    #print (f"cmd={cmd}, arg={arg}") 
    if cmd and  re.match("^-[a-zA-Z]?", arg): self.complete_type="sopt"
    if cmd and  re.match("^--([a-zA-Z]\w)?", arg): self.complete_type="lopt"
    if self.complete_type=="group":
      m=self.get_group_list(arg)
    elif self.complete_type=="group_entry" or self.complete_type=="entry_group":
      m=["group", "entry"]
    elif self.complete_type=="entry":
      m=["entry"]
    elif self.complete_type=="cmd":
      m=list(self.cmds.keys())
    elif self.complete_type=="sopt":
      try:
        m=self.cmds[cmd]['sopts']
      except:
        pass
    elif self.complete_type=="lopt":
      try:
        m=self.cmds[cmd]['lopts']
      except:
        pass
    #print(m)
    self.poss_match=m
    
  def get_cur_before(self):
    idx = readline.get_begidx()
    full = readline.get_line_buffer()
    r=full[:idx]
    #print (r)
    return r

  def get_cur_arg(self):
    idx = readline.get_begidx()
    full = readline.get_line_buffer()
    r=full[idx:]
    #print (r)
    return r


  def completer(self, text, state):
    pref = self.get_cur_before()
    n = pref.split()
    cmd=None
    if len(n)==0:
      self.complete_type=self.complete_type_def
    else:
      for cnt, arg in enumerate(n):
        #print(f"cmd: {cmd}, cnt: {cnt}, arg: {arg}")
        if cnt==0:
          cmd=arg
          self.complete_type=self.cmds[cmd]['complete_type']
        else:
          #if re.match("^-\w?", arg): self.complete_type="sopt"
          #elif re.match("^--\w?", arg): self.complete_type="lopt"
          pass

            
    self.set_poss_match(self.get_cur_arg(), cmd)          
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
      #else:
      ##  print(self.resolve_path(i))

a=hkpi()
a.run() 
