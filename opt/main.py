##############################
#      ライブラリインポート     #
##############################
import codecs
import os
import sys
import datetime
import tkinter as tk
import tkinter.simpledialog as sd
import math

#グローバル変数
fname = '=====text2.txt' #ソースコードのファイル名
_spt = 0 #ソース読取ポインタ
fnno = 0
sourceCode = '' #CR、LFを取り除いてEOLを入れた文字列のリスト
_chkMode = 0 #文法チェック時は1にする
_sline = 0 #読取中のsourceCodeの行
_line = 0 #読み取り中のInterCodeの行
_lpt = 0 #行内のポインタ
InterCode = [] #中間コード
GVARSIZE = 0
MEMSIZE = 2 ** 10
Dmem = [0.0] **MEMSIZE #メインメモリの確保
errmsg0 = '構文エラー 行 = '
_fnno = 0 #実行中の関数の番号
fExit = 0
fBreak = 0
fReturn = 0
fElif = 0
fElse = 0
fEnd = 0
callParaList = [] #関数コール時、戻り値などを保存する
LTable = [] #ローカル変数テーブル
GTable = [] #グローバル変数テーブル
VTable = [] #数値テーブル
STable = [] #文字列テーブル
FTable = [] #関数テーブル
FTable1 = [] #関数名だけを先に取得
DTable = [] #配列テーブル
DArray = [] #配列の実体 125
baseReg = 0
spReg = 0
funcAddrList = [] #関数の開始、終了行のペアを格納
localVarSize = [] #各関数内のローカル変数のサイズ
fnnoList = [] #各行が何番の関数に属しているか
ifEndList = [] #ifに対応するendの行番号のリスト
breakList = []

#####################################
#     トークンの種類、中間コード        #
#####################################

While = 0
Func = 1
If = 2
Else = 3
Elif = 4
End = 5
Plus = 6
Minus = 7
Mult = 8
Div = 9
Assign = 10
Comma = 11
Db1Q = 12
Dot = 13
Equal = 14
NotEq = 15
Less = 16
LessEq = 17
Great = 18
GreatEq = 19
EOT = 20
EOL = 21
EOF = 22
LParen = 23
RParen = 24
LBracket = 25
RBracket = 26
Mod = 27
Doll = 28
Under = 29
Sg1Q = 30
Comment = 31
PlusEq = 32
MinusEq = 33
MultEq = 34
DivEq = 35
Db1Num = 36
Str = 37
Digit = 38
Letter = 39
Not = 40
Ident = 41
Print = 42
For = 43
To = 44
Break = 45
Return = 46
Exit = 47
And = 48
Or = 49
Fcall = 50
Lvar = 51
Gvar = 52
Pow = 53
Step = 54
Input = 55
Rfile = 56
Wfile = 57
Toint = 58
Sin = 59
Cos = 60
Tan = 61
Dim = 62 #配列の定義
Dvar = 63 # 配列変数の中間コード用
IDiv = 64 #整数の商
Dsin = 65
Dcos = 66
Dtan = 67

cEOL = chr(EOL)

#キーワードテーブル

KWTbl =\
    [['while',  While, ''],
     ['func',   Func,   ''],
     ['if',     If,     ''],
     ['else',   Else,   ''],
     ['elif',   Elif,   ''],
     ['end',    End,    ''],
     ['+',      Plus,   ''],#6
     ['-',      Minus,  ''],
     ['*',      Mult,   ''],
     ['/',      Div,    ''],
     ['=',      Assign, ''],#10
     [',',      Comma,  ''],
     ['"',      DblQ,   ''],
     ['.',      Dot,    ''],
     ['==',     Equal,  ''],#14
     ['!=',     NotEq,  ''],
     ['<',      Less,   ''],
     ['<=',     LessEq, ''],
     ['>',      Great,  ''],
     ['>=',     GreatEq,    ''],
     ['EOT',    EOT,    ''],#20
     ['EOL',    EOL,    ''],
     ['EOF',    EOF,    ''],
     ['(',      LParen, ''],
     [')',      RParen, ''],
     ['[',      LBracket,   ''],
     [']',      RBracket,   ''],
     ['//',     IDiv,    ''], #整数の商
     ['$',      Doll,   ''],
     ['_',      Under,  ''],
     ["'",      SglQ,   ''],#30
     ['#',     Comment,    ''],#31
     ['+=',     PlusEq, ''],
     ['-=',     MinusEq,    ''],
     ['*=',     MultEq, ''],
     ['/=',     DivEq,  ''],#35
     ['DblNum', DblNum, ''],
     ['Str',    Str,    ''],
     ['Digit',  Digit,  ''],
     ['Letter', Letter, ''],
     ['!',      Not,    ''],
     ['Ident',  Ident,  ''],#41
     ['print',  Print,  ''],
     ['for',    For,    ''],
     ['to',     To,     ''],
     ['break',  Break,  ''],
     ['return', Return, ''],
     ['exit',   Exit,   ''],
     ['and',    And,    ''],
     ['or',     Or,     ''],
     ['Fcall',  Fcall,  ''],
     ['Lvar',   Lvar,   ''],
     ['Gvar',   Gvar,   ''],#52
     ['**',     Pow,    ''],#53
     ['step',   Step,   ''],#54
     ['input',  Input,   ''],#55
     ['rfile',  Rfile,   ''],#56
     ['wfile',  Wfile,   ''],#57
     ['toint',  Toint,   ''],#58
     ['sin',    Sin,   ''],#59
     ['cos',    Cos,   ''],#60
     ['tan',    Tan,   ''],#61
     ['dim',    Dim,   ''],#62
     ['Dvar',   Dvar,   ''],#63
     ['%',      Mod,   ''],#64 剰余
     ['dsin',   Dsin,   ''],
     ['dcos',   Dcos,   ''],
     ['dtan',   Dtan,   ''],
    ]