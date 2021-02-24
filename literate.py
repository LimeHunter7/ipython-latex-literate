# -*- coding: utf-8 -*-
from IPython.core.latex_symbols import latex_symbols, reverse_latex_symbol
import unicodedata as ud
from dataclasses import dataclass
import pandas as pd
from textwrap import wrap
import codecs


@dataclass
class Character:
    character: str
    category: str = None
    name: str = None
    ipython_cmd: str = None
    latex_cmd: str = None

    def __post_init__(self):
        if self.category is None:
            self.category = ud.category(self.character)
            self.name = ud.name(self.character)
        if self.ipython_cmd is None:
            try:
                self.ipython_cmd = reverse_latex_symbol[self.character]
            except KeyError:
                pass

    def __str__(self):
        return ' '.join((self.character, self.category, self.name,
                         self.ipython_cmd))


BF_CMD = r'\bm{{{{{}}}}}'  # package bm
IT_CMD = r'\mathit{{{}}}'
SCR_CMD = r'\mathcal{{{}}}'  # package mathalpha boondox
FRAK_CMD = r'\mathfrak{{{}}}'  # package amsfonts
BB_CMD = r'\mathbb{{{}}}'  # package mathalpha boondox
SANS_CMD = r'\mathsf{{{}}}'
ISANS_CMD = r'\mathsfit{{{}}}'  # newcommand
TT_CMD = r'\mathtt{{{}}}'
N_CMD = r'\mathrm{{{}}}'


upgreek_blacklist = ('Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma',
                     'Upsilon', 'Phi', 'Psi', 'Omega', 'varkappa', 'varTheta')


def latex_char(char: Character, prefix: str) -> str:
    if char.category[1] == 'd':
        return ud.digit(char.character)
    ipc = char.ipython_cmd
    # TODO: special-case upgreek in bf
    suffix = ipc[len(prefix):]
    if len(suffix) > 1:
        if prefix in ('\\', r'\bf') and suffix not in upgreek_blacklist:
            suffix = 'up' + suffix
        elif (prefix in (r'\it', r'\bi') and suffix in upgreek_blacklist
              and 'var' not in suffix):
            suffix = 'var' + suffix
        suffix = '\\' + suffix
    return suffix


def add_cmd(char: Character) -> bool:
    ipc = char.ipython_cmd
    cmd = None
    if ipc[1] in ('^', '_'):
        cmd = '{}' + ipc[1] + latex_char(char, ipc[:2])
    # We Enjoy Typing
    elif ipc.startswith(r'\tt'):
        cmd = TT_CMD.format(latex_char(char, ipc[:3]))
    elif ipc.startswith(r'\bisans'):
        cmd = BF_CMD.format(ISANS_CMD.format(latex_char(char, r'\bisans')))
    elif ipc.startswith(r'\isans'):
        cmd = ISANS_CMD.format(latex_char(char, r'\isans'))
    elif ipc.startswith(r'\bsans'):
        cmd = BF_CMD.format(SANS_CMD.format(latex_char(char, r'\bsans')))
    elif ipc.startswith(r'\sans'):
        cmd = SANS_CMD.format(latex_char(char, r'\sans'))
    elif ipc.startswith(r'\bfrak'):
        cmd = BF_CMD.format(FRAK_CMD.format(latex_char(char, r'\bfrak')))
    elif ipc.startswith(r'\bbi') and ipc != r'\bbi':
        # TODO
        return False
    elif ipc.startswith(r'\bb'):
        cmd = BB_CMD.format(latex_char(char, r'\bb'))
    elif ipc.startswith(r'\frak'):
        cmd = FRAK_CMD.format(latex_char(char, r'\frak'))
    elif ipc.startswith(r'\bscr'):
        cmd = BF_CMD.format(SCR_CMD.format(latex_char(char, r'\bscr')))
    elif ipc.startswith(r'\scr'):
        cmd = SCR_CMD.format(latex_char(char, r'\scr'))
    elif ipc.startswith(r'\bi'):
        cmd = BF_CMD.format(IT_CMD.format(latex_char(char, r'\bi')))
    elif ipc.startswith(r'\bf'):
        cmd = BF_CMD.format(N_CMD.format(latex_char(char, r'\bf')))
    elif ipc.startswith(r'\it'):
        cmd = IT_CMD.format(latex_char(char, r'\it'))
    elif not char.name.startswith('MATHEMATICAL'):
        if char.name.startswith('GREEK'):
            cmd = latex_char(char, '\\')
        else:
            print(f'Assuming ipython got it right: {char}')
            cmd = ipc
    else:
        return False
    char.latex_cmd = r'\(' + cmd + r'\)'
    return True


# https://www.unicode.org/charts/PDF/U1D400.pdf
greek_blacklist = {'Alpha', 'Beta', 'Epsilon', 'Zeta', 'Eta', 'Iota', 'Kappa',
                   'Mu', 'Nu', 'Omicron', 'omicron', 'Rho', 'Tau', 'Chi',
                   'Stigma', 'Digamma', 'digamma', 'Koppa', 'Sampi',
                   'varTheta'}

chars = []
for _, c in latex_symbols.items():
    char = Character(c)
    if char.category not in {'Lu', 'Ll', 'Lm', 'Nd'}:
        # print(f'exclude {c} {cat} {name}')
        # exclude ℘ Sm SCRIPT CAPITAL P
        # exclude ℵ Lo ALEF SYMBOL
        # exclude ℶ Lo BET SYMBOL
        # exclude ℷ Lo GIMEL SYMBOL
        # exclude ℸ Lo DALET SYMBOL
        continue
    sname = char.name.split()
    if sname[0] == 'LATIN':
        if sname[1] == 'SUBSCRIPT' and sname[-1] != 'SCHWA':
            # subscript latin
            pass
        elif char.category == 'Lm' and sname[-1] != 'SCHWA':
            # superscript latin
            pass
        else:
            # print(f'exclude {c} {cat} {name}')
            # exclude ħ Ll LATIN SMALL LETTER H WITH STROKE
            continue
    if sname[-2] not in {'LETTER', 'CAPITAL', 'SMALL', 'DIGIT'}:
        if char.ipython_cmd.startswith(r'\^'):
            # superscript greeks
            pass
        elif sname[-1] == 'SYMBOL':
            # variant greeks
            if sname[-2] == 'EPSILON':
                char.ipython_cmd.replace('epsilon', 'varepsilon')
            pass
        elif sname[-2] == 'FINAL':
            # varsigma
            pass
        else:
            # print(f'exclude {char}')
            continue
    if sname[0] in ('GREEK', 'MATHEMATICAL'):
        # exclude confusable/weird greeks
        ipc = char.ipython_cmd
        if not ipc.endswith('upsilon') and 'up' in ipc:
            # print(f'exclude {char}')
            if ipc == r'\upepsilon':
                char.ipython_cmd = r'\epsilon'
            else:
                continue
        if any(ipc.endswith(g) for g in greek_blacklist):
            # print(f'exclude {char}')
            continue
        if (sname[1] == 'SANS-SERIF' and len(sname[-1]) > 1
                and sname[-2] != 'DIGIT'):
            # exclude sans-serif greeks
            # TODO
            # print(f'exclude {char}')
            continue
    if sname[0] == 'TURNED':
        # exclude turned capital F
        continue
    if sname[-1] == 'APOSTROPHE':
        # print(f'exclude {char}')
        # exclude ʼ Lm MODIFIER LETTER APOSTROPHE \rasp
        # arguably this could be useful to prime something? quel horreur tho
        continue
    # finally time to add the commands
    if not add_cmd(char):
        print(f'no command! {char}')
        # no command! ⅅ Lu DOUBLE-STRUCK ITALIC CAPITAL D \bbiD
        # no command! ⅆ Ll DOUBLE-STRUCK ITALIC SMALL D \bbid
        # no command! ⅇ Ll DOUBLE-STRUCK ITALIC SMALL E \bbie
        # no command! ⅈ Ll DOUBLE-STRUCK ITALIC SMALL I \bbii
        # no command! ⅉ Ll DOUBLE-STRUCK ITALIC SMALL J \bbij
        continue
    chars.append(char)

# patch in the annoying ones
for c in ('ħ', 'ℵ', 'ℶ', 'ℷ', 'ℸ'):
    char = Character(c)
    char.latex_cmd = r'\(' + char.ipython_cmd + r'\)'
    chars.append(char)

df = pd.DataFrame(chars)

literate = r'\lstset{extendedchars=true,literate='
literate += ' '.join(f'{{{char.character}}}{{{{{char.latex_cmd}}}}}1'
                     for char in chars)
literate += '}'
with codecs.open('literate.tex', 'w', 'utf-8') as f:
    f.write(literate)

with codecs.open('literate_test.txt', 'w', 'utf-8') as f:
    f.write('\n'.join(wrap(''.join(char.character for char in chars))))
