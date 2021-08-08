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
DblQ = 12
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
SglQ = 30
Comment = 31
PlusEq = 32
MinusEq = 33
MultEq = 34
DivEq = 35
DblNum = 36
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

###############################
#     キーワードテーブル         #
###############################

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

#########################################
#     関数テーブルFTable[]に格納するクラス   #
#########################################

class FTableData :
    def __init__(self,name,line,endLine = -1, fnno = -1, argList = []) :
        self.name = name
        self.endLine = endLine
        self.fnno = fnno
        self.argList = argList #LTable[]内のインデックスのリスト

##########################################
# push(),pop()を使えるようにしたクラス       #
##########################################

class Stack :
    def __init__(self) :
        self.stack = []
    def push(self,x) :
        self.stack.append(x)
    def pop(self) :
        return self.stack.pop
    def size(self) :
        return len(self.stack)

opstack = stack() # 数式評価用のオペランドスタック

###########################################
#     文字列の登録を確認する                  #
###########################################

class Token :
    def __init__(self,kind,val,name,idx = 0) :
        #インスタンス変数の提議
        self.kind = kind # DblNumなど
        self.val = val # 45.3など
        self.name = name # whileなど
        self.idx = idx #文字列の登録インデックスなど
    def print(self) :
        print('kind = {}\nval = {}\nname = {}\nidx = {}\n'.format(self.kind,self.val,self.name,self.idx))

############################################
#       変数の登録リストに入れるクラス          #
############################################

class Var :
    def __init__(self,name,fnno,len,dmmaddr,val,line,idx) :
        self.name = name
        self.fnno = fnno
        self.len = len
        self.dmmaddr = dmmaddr
        self.val = val
        self.line = line
        self.idx = idx

######################################################
#       文字列でソースを行に分割し、sourceCodeへ入れる     #
#       CR,LFなどOSにより違う                          #
#       空行は#のみの行として扱う                        #
######################################################

def getLines(splt) :
    global sourceCode
    wk = source.split(splt)
    for i in range(len(wk)) :
        wk[i] = wk[i].lstrip() #文字列の左の空白を削除
        if len(wk[i]) == 0 :
            wk[i] = '#' #空白はコメント行として扱う
        wk[i] += cEOL
    sourceCode = wk

######################################################
#           ソースを一括リード                          #
######################################################

def readSource(fname) :
    f = codecs.open(fname,'r','utf-8')
    s = f.read()
    f.close()
    return s

##############################################################
#          fnnoList[]に各行の fnno を入れる                    #
#          ソースの先頭から、見つかった関数に番号（fnno）をつける    #
#          関数に属していない行はfnno = 0                       #
##############################################################

def getFnnoList() :
    global fnnoList, _lpt, funcAddrList, FTable1
    FTable1.clear()
    fnnoList.clear()
    funcAddrList = []
    stk = Stack()
    for line in range(len(sourceCode)) :
        _lpt = 0
        tkn = getToken1(line)
        kd = tkn.kind
        if kd == Func or kd == If or kd == For or kd == While :
            stk.push([kd, line]) 
            if kd == Func :
                tkn = getToken1(line) #関数名も取得しておく
                for i in range(len(FTable1)): #同じ関数名があればエラー
                    if FTable1[i][1] == tkn.val :
                        raise Exception(errmsg0 + str(line + 1))
                FTable1.append([line, tkn.val])
        elif kd == End :
            x = stk.pop()
            if x[0] == Func :
                funcAddrList.append([x[1], line]) #定義開始、終了行
    for i in range(len(sourceCode)) :
        fnnoList.append(0)
    #ソースの各行がどの関数に属しているかfnnoを記録
    k = 1
    for i in range(len(funcAddrList)) :
        [x, y] = funcAddrList[i]
        for j in range(x, y + 1) :
            fnnoList[j] = k
        k = k + 1
    return

########################################################
#           次のトークンを取得し、sと一致しているか確認       #
#           一致しなければ例外を発生させる                  #
########################################################

def nextTkn(line, s) :
    x, y = getToken2(line)
    if x != s :
        raise Exception(errmsg0 + str(line + 1))

##########################################################
#           _lpt（行内のポインタ位置)から1個、トークンを取得    #
##########################################################

def getToken1(line) :
    global _sline
    _sline = line
    skipSpaceLine()
    c = getc()
    s = c
    #DblNum1文字目
    if ('0' <= c and c <= '9') or c == '.' : 
        x = numVal(c)
        registVal(Token(DblNum, x, '')) #kind, val, name
        return Token(DblNum, x, '') #読み取ったトークンを返す。数値を表すトークン。
    #ローカル変数、グローバル変数、関数名の1文字目
    if ('A' <= c and c <= 'Z') \
                or ('a' <= c and c <= 'z') or c == '_' or c == '$' :
         #'$'はグローバル変数名の先頭
        s = getIdent(c)
        idx = getKwtblIndex(s)
        if idx >= 0 : #予約語なら
            return Token(KWTbl[idx][1], KWTbl[idx][0], '')
        elif c != '$' :#ローカル変数名か関数名
            return Token(Lvar, s, '') #予約語でないIdent   
        else : #'$'で始まる(グローバル変数名)
            for i in range(len(DTable)):
                if DTable[i].name == s : #配列変数名だった
                    return Token(Dvar, s, '', i) #インデックスiも返す
            registGvar(Token(Gvar, s, ''), line)
            return Token(Gvar, s, '') #予約語でないIdent   
    #+, - や += , == など
    if c == '+' or c == '-' or c == '='\
               or c == '!' or c == '>' or c == '<' :
        s = getOp1(c) #cで始まるトークンの文字列を取得
        idx = getKwtblIndex(s) #sからキーワードテーブル(KWTble)のインデックスを得る
        return Token(KWTbl[idx][1], KWTbl[idx][0], '')
    elif c == '*' or c == '/': # **,//
        s = getOp2(c)
        idx = getKwtblIndex(s)
        return Token(KWTbl[idx][1], KWTbl[idx][0], '')
    #1文字でトークン確定
    if c == '"' or c == '(' or c == ')' or c == ','\
                or c == '[' or c == ']'or c == '#' or c == '%' :
        s = c
        idx = getKwtblIndex(s)
        if c == '"' : #ダブルクォーテーションなら
            idx = registStr() #STableに登録したインデックスが返る
            return Token(Str, '', '', idx)            
        return Token(KWTbl[idx][1], KWTbl[idx][0], '')
    if c == cEOL :
        return None
    raise Exception(errmsg0 + str(line + 1)) #トークンを判断できなかった

#################################################################################
#              dimの処理専用（配列登録用）                                          #
#              _lpt（行内のポインタ位置)から1個トークン(文字か文字列か数値)を取得         #
#              13,DblNum などのペアを返す                                          #
#################################################################################

def getToken2(line) :
    global _sline
    _sline = line
    skipSpaceLine()
    c = getc()
    s = c
    #DblNum1文字目
    if ('0' <= c and c <= '9') or c == '.' : 
        x = numVal(c)
        return x, DblNum
    #Ident1文字目
    elif ('A' <= c and c <= 'Z') \
                or ('a' <= c and c <= 'z') or c == '_' or c == '$' :
        #'$'はグローバル変数名の先頭
        s = getIdent(c)
        if c != '$' : #Identのうち、ローカル変数名
            raise Exception(errmsg0 + str(line + 1))
        return s, Gvar
    elif c == '[' or c == ']'or c == ',' :
        return c, 0
    elif c == cEOL :
        return None, 0
    raise Exception(errmsg0 + str(line + 1)) #トークンを判断できなかった

################################################################
#        Tokenのインスタンス変数   kind, val, name, idx           #
#        KWTbl[idx][1] = 'while', KWTbl[idx][0] = While など    #
#--------------------------------------------------------------#
#sourceCodeの現在の行内で、_lpt位置からスペースをスキップ             #
################################################################

def skipSpaceLine() :
    global _lpt
    c = getc()
    if c != ' ' :
        _lpt -= 1
        return
    while c == ' ' :
        c = getc()
    _lpt -= 1
    return

#################################################################
#         sourceCode[]からポインタ(_sline, _lpt)位置の1文字をリード  #
#         ポインタは行内で動くだけ、_slineは動かさない                # 
#################################################################

def getc() :
    global _lpt
    c = sourceCode[_sline][_lpt]
    _lpt += 1
    return c

#################################################################
#          先頭が文字cの数値を1個sourceCodeから得る                  #
#          _lpt はその数値の末位の次の桁を指した状態で返る             #
#################################################################

def numVal(c) :
    global _lpt
    s = ''
    ct = 0
    while ('0' <= c and c <= '9') or c == '.' :
        if c == '.' :
            ct += 1
            if ct >= 2 : #カンマが2つ以上あればエラー
                raise Exception(errmsg0 + str(_sline + 1))
        s += c
        c = getc()
    #0～9か.以外の文字が出てきたらここへ来る
    _lpt -= 1
    return float(s)

#################################################################
#       現在のポインタ位置から +=, -=, ==, !=, +, -, =, ! を得る     #
#################################################################

def getOp1(c) :
    global _lpt
    s = c
    c1 = getc() #次の文字
    if c1 == '=': #+=,-=,==,!=,<=,>=
        s = s + c1
    else: #+,-,=,!,<,>
        _lpt -= 1
    return s
#################################################################
#        現在のポインタ位置から **, //, *, /, *=, */ を得る          #
#################################################################

def getOp2(c) :
    global _lpt
    s = c
    c1 = getc() #次の文字
    if c1 == '=' :
        s = s + c1
        return s # *=, /=
    if c == c1 :
        s = c + c1 # **, //
    else :
        s = c
        _lpt -= 1
    return s

#################################################################
#    文字列 s をキーワードテーブル（KWTbl）から探してインデックスを返す   #
#################################################################

def getKwtblIndex(s) :
    for i in range(len(KWTbl)) :
        if KWTbl[i][0] == s :
            return i
    return -1

###############################################
#      InterCode[line]に「n」を追加             #
###############################################

def addCode(line, n) :
    InterCode[line].append(float(n))

################################################
#      sourceCodeからInterCodeへ変換             #
################################################

def toInterCode():
    for i in range(len(sourceCode)) :
        toInterCode1(i)

################################################
#      sourceCodeからInterCodeへ1行分変換        #
################################################

def toInterCode1(line) :
    global _lpt
    InterCode.append([]) #新しい行のためのリスト
    _lpt  = 0
    while True :
        ret, tkn = toInterCode0(line)
        if ret == True :
            break #1行終わった

##########################################################
#     ソースコードを中間コードに変換                          #
#     1回のコールでトークン1個分を中間コードに変換              #
#     SourceCode[line]からInterCode[line]へ           　  #
#     while → While, 終了行 や　関数名 → Func, 変数名　など 　#
#　　　InterCodeは各行とも最後にcEOL(行末のマーク)は入れない    #
#     戻り値が False ならその行にはまだトークンが続く         　#
##########################################################

def toInterCode0(line) :
    tkn = getToken1(line)
    if tkn == None : #cEOL(行の最後)だったら
        return True, tkn
    kd = tkn.kind
    addCode(line, kd) #Lvar, DblNumなどをInterCodeへappend
    if kd == While or kd == If or kd == Elif or kd == Else or kd == For :
        #あとでここにendの存在する番地などを入れるため、空けておく
        addCode(line, 123456) #パディング
        if kd == If or kd == Elif or kd == Else : #if, elif, else では2回パディング
            addCode(line, 7890) #パディング
    elif kd == Lvar :
        for i in range(len(FTable1)) : #FTable1[]は予め調べておいた関数名のリスト
            if FTable1[i][1] == tkn.val : #関数名だったら
                InterCode[line][-1] = Fcall #関数呼び出しに書き直す
                addCode(line, i) #Fcallのすぐ後には関数のインデックスを格納
                return False, tkn
        #Var  name, fnno, len, dmmaddr, val, line, idx
        v = Var(tkn.val, fnnoList[line], 1, -1, -1, line, -1)
        j = registLvar(v) #関数の引数以外のローカル変数を登録
        addCode(line, j)
    elif kd == Gvar :
        tkn.kind = Gvar
        j = registGvar(tkn, line) #すでに登録済みの変数だが、jを得るためにコール
        addCode(line, j) #GTable[j]の変数であることをInterCodeに記録
    elif kd == Dvar :
        tkn.kind = Dvar
        addCode(line, tkn.idx) #この配列変数はDTable[tkn.idx]に登録してある
    elif kd == DblNum :
        tkn.kind = DblNum
        j = registVal(tkn) #すでに登録済みの変数だが、jを得るため
        addCode(line, j) #VTable[j]の変数であることをInterCodeに記録
    elif kd == Str :
        addCode(line, tkn.idx) #STable内のindexを中間コードとする
    elif kd == Break :
        addCode(line, 2222) #パディング。Breakの次にbreak実行後の飛先を入れるため。
    elif kd == Func :
        registFunc(line)
    elif kd == Comment : #「#」より後ろの部分は中間コードにしない
        return True, tkn
    elif kd == Dim : #dimより後ろの部分は中間コードにしない
        return True, tkn
    return False, tkn #False……続きがある

###########################################################
#     STableに登録後、保存位置（STableのインデックス）を返す     #
#     登録済みだったらインデックスだけ求めて返す                 #
###########################################################

def registStr() :
    s = ''
    c = getc()
    while c != '"' and c != cEOL :
        s += c
        c = getc()
    for i in range(len(STable)) :
        if STable[i] == s :
            return i
    STable.append(s)
    return len(STable) - 1 #indexを返す

##########################################################
#     数値の登録 トークンを保存する                  　       #
#     VTableに登録後、保存位置（VTableのインデックス）を返す    #
#     登録済みだったらインデックスだけ求めてそれを返す           #
##########################################################

def registVal(tkn) :
    global VTable
    for i in range(len(VTable)) :
        if VTable[i].val == tkn.val :
            return i #登録済みだった
    VTable.append(tkn)
    j = len(VTable) - 1 #今、追加したデータのインデックス
    return j #登録した    

###########################################################
#    グローバル変数の登録                                   　#
#    GTableに登録後、変数の保存位置（GTableのインデックス）を返す　#
#    登録済みの変数だったらインデックスだけ求めてそれを返す    　 　#
###########################################################

def registGvar(tkn, line) :
    global GTable, GVARSIZE
    for i in range(len(GTable)) :
        if GTable[i].name == tkn.val :
            return i #登録済みだった
    v = Var(tkn.val, 0, 1, 0, 0, 0, 0) #name, fnno, len, dmmaddr, val, line, idx
    GTable.append(v)
    j = len(GTable) - 1
    GTable[j].dmmaddr = GVARSIZE #ここまでのGvarの個数の計
    GVARSIZE += v.len #更新
    return j #登録した

####################################################################
#     ローカル変数の登録                                              #
#     LTable内の変数の保存位置を返す                                   #
#     LTableに登録後、変数の保存位置（LTableのインデックス）を返す         #
#     登録済みの変数だったらインデックスを求めて返す                       #
####################################################################

def registLvar(v) :
    global LTable
    for i in range(len(LTable)) :
        if LTable[i].name == v.name and LTable[i].fnno == v.fnno :
            return i #登録済みだった
    LTable.append(v)
    j = len(LTable)-1 #今、追加した変数のインデックス
    return j #登録した

###################################################################
#     配列変数の登録                                          　　   #
#     エラーなら例外発生                                     　　     #
#                                                                 #
#     dim $a[10], $bbb[30], $cc[15]　のよう1行にまとめて書いてもよい  　#
#     kind, val, name, idx                                        #
###################################################################

def registDvar() :
    global DTable, _sline, _lpt
    _sline = 0
    for line in range(len(sourceCode)) :
        _lpt = 0
        tkn = getToken1(line)
        if tkn.kind == Dim :
            registDvar1(line)

###########################################################
#     配列変数の登録                               　      　#
#     dimを読んでからここへ来る                          　   #
#     エラーなら例外発生                                     #
#                                                      　 #
#     dim $a[10], $bbb[30], $cc[15]   　　　   　          #
#     kind, val, name, idx             　 　　 　      　   #
###########################################################

def registDvar1(line) :
    global DTable, _lpt, DArray
    while True :
        varname, kind = getToken2(line) #グローバル変数名
        if kind != Gvar :
            raise Exception(errmsg0 + str(line + 1))
        nextTkn(line, '[') #'['のはず
        varsize, kind = getToken2(line)  #配列のサイズ（数値）
        if kind != DblNum :
            raise Exception(errmsg0 + str(line + 1))
        nextTkn(line, ']') #']'のはず
        for i in range(len(DTable)) :
            if DTable[i].name == varname: #既に登録されている変数名ならエラー
                raise Exception(errmsg0 + str(line + 1))
        v = Var(varname, fnnoList[line], varsize, 0, 0, line, len(DTable))
        #name, fnno, len, dmmaddr, val, line, idx
        DTable.append(v)
        #配列の領域確保
        lst = [] #126
        for i in range(int(varsize)) :
            lst.append(0)
        DArray.append(lst)
        c, d = getToken2(line)
        if c == None :
            _lpt -= 1
            return #無事、配列の定義が終了
        elif c != ',' :
            raise Exception(errmsg0 + str(line + 1))
        #カンマだった