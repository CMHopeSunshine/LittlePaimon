#!/usr/bin/env python
# -*-coding:utf-8 -*-
from hoshino.typing import List, Dict

# {
#     语言的名字: [语言的别名], ...
# }
language_list: Dict[str, List[str]] = {
    'assembly': ['assembly', 'asm'],
    'ats': ['ats'],
    'bash': ['bash'],
    'c': ['c'],
    'clojure': ['clojure'],
    'cobol': ['cobol'],
    'coffeescript': ['coffeescript'],
    'cpp': ['cpp', 'c++'],
    'crystal': ['crystal'],
    'csharp': ['csharp', "c#"],
    'd': ['d'],
    'elixir': ['elixir'],
    'elm': ['elm'],
    'erlang': ['erlang'],
    'fsharp': ['fsharp'],
    'go': ['go'],
    'groovy': ['groovy'],
    'haskell': ['haskell'],
    'idris': ['idris'],
    'java': ['java'],
    'javascript': ['javascript', 'js'],
    'julia': ['julia'],
    'kotlin': ['kotlin'],
    'lua': ['lua'],
    'mercury': ['mercury'],
    'nim': ['nim'],
    'nix': ['nix'],
    'ocaml': ['ocaml'],
    'perl': ['perl'],
    'php': ['php'],
    'python': ['python', 'py', 'python3'],
    'raku': ['raku'],
    'ruby': ['ruby'],
    'rust': ['rust'],
    'scala': ['scala'],
    'swift': ['swift'],
    'typescript': ['typescript', 'ts']
}

# {语言名: 文件后缀名}
suffix_list: Dict[str, str] = {
    'assembly': "asm",
    'ats': "dats",
    'bash': "sh",
    'c': "c",
    'clojure': "clj",
    'cobol': "cob",
    'coffeescript': "coffee",
    'cpp': "cpp",
    'crystal': "cr",
    'csharp': "cs",
    'd': "d",
    'elixir': "ex",
    'elm': "elm",
    'erlang': "erl",
    'fsharp': "fs",
    'go': "go",
    'groovy': "groovy",
    'haskell': "hs",
    'idris': "idr",
    'java': "java",
    'javascript': "js",
    'julia': "jl",
    'kotlin': "kt",
    'lua': "lua",
    'mercury': "m",
    'nim': "nim",
    'nix': "nix",
    'ocaml': "ml",
    'perl': "pl",
    'php': "php",
    'python': "py",
    'raku': "raku",
    'ruby': "rb",
    'rust': "rs",
    'scala': "scala",
    'swift': "swift",
    'typescript': "ts"
}

# 查询列表, 应该有更好的实现方式, 但是语言比较少, 就先这样了
# 变成{"py": "python", "python3": "python", "python":"python", ...}的结构
search_dict = {}
for key, value in language_list.items():
    for alias in value:
        search_dict[alias] = key
