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

################################################################################
#    Func f1(x, y)の行の処理                                 　                  #
#    関数名、引数などを FTable[] に登録する                                       　#
#    Func を読み終わった状態でコールする                                            #
#    Funcの後に2データ(関数の終了行、FTable[]内のインデックス)、InterCodeに記録済み     #
#    関数の番号 fnno はFTable[]のインデックスとは異なる                              #
#    fnnoは定義された順に1,2,3,……。と連番を振る                                     #
#    class FTableData:                                                         #
#    def __init__(self, name, line, endLine = -1, fnno = -1, argList = []):    #
################################################################################

def registFunc(line) :
    argList = [] #関数の引数リスト。LTable[]のインデックスを入れる。FTable[]に格納。
    tkn = getToken1(line) #関数名
    fname = tkn.val #'f1'など
    endLine = searchFuncAddr(line)
    if endLine == -1 :
        raise Exception(errmsg0 + str(line + 1))
    addCode(line, endLine) #Funcのすぐ後に対応するendのアドレスを入れる
    addCode(line, 4444) #定義された関数のインデックスを後で入れるため。
    fdata = FTableData(fname, line, endLine, fnnoList[line]) #クラスに値をセット
    #name, line, endLine = -1, fnno = -1, argList = []
    if not checkCode(line, LParen): #次のトークンが LParen であることを確認
        raise Exception(errmsg0 + str(line + 1))
    addCode(line, LParen)
    tkn = getToken1(line)
    if tkn.kind == RParen:
        addCode(line, RParen) #変数なし、右括弧で終わり
        #変数なしの関数の登録
        fdata.argList = argList
        FTable.append(fdata) #関数の登録
        return True
    #')'でなかった
    while True:
        if tkn.kind != Lvar : #それはLvarでなければ
            raise Exception(errmsg0 + str(line + 1))
        #tknはローカル変数だった
        addCode(line, Lvar)
        #Var  name, fnno, len, dmmaddr, val, line, idx
        v = Var(tkn.val, fnnoList[line], 1, -1, -1, line, -1)
        j = registLvar(v) #LTable[j]に関数の引数であるローカル変数が格納される
        argList.append(j)
        addCode(line, j) #InterCodeのLvarの次にjを格納
        tkn = getToken1(line)
        if tkn == None:
            raise Exception(errmsg0 + str(line + 1))
        if tkn.kind == RParen: #右括弧なら無事終わり
            addCode(line, RParen)
            fdata.argList = argList
            FTable.append(fdata) #関数の登録
            InterCode[line][2] = len(FTable) - 1 #関数はFTable内のここへ登録された
            return True
        elif tkn.kind != Comma: #それはコンマでなければ終わり
            raise Exception(errmsg0 + str(line + 1))
        addCode(line, Comma)
        tkn = getToken1(line)

#########################################################
#   次のトークンの kind（While, For など） が kd ならTrue    #
#########################################################

def checkCode(line, kd) :
    tkn = getToken1(line)
    if tkn.kind == kd :
        return True
    return False

############################################################################
#    line 行目で定義されている関数の引数のリストを得る                          　 #
#   （LTable[]内のインデックスのリスト）                                      　#
#    関数名は最初に中間コード生成時に Lvar, idx とされている               　   　 #
#    中間コードは                                                            #
#     Func, _, _, Lvar, idx, LParen, Lvar, _, Comma, Lvar, _, Comma, ……    #
#    という並びになっている                                                    #
#    Lvar, idx は以降では使わないが、詰めずに放っておく                           #
#    関数の引数は 行の先頭 +6 から 引数がなければ +6 にはRParenがある              #
############################################################################

def getArgList(line) :
    ret = []
    if lookIc(line, 6) == RParen :
        return []
    ret.append(lookIc(line, 7)) #Lvar のLTable[]内でのインデックス
    i = 8
    while lookIc(line, i) != RParen :
        ret.append(lookIc(line, i + 2)) #Lvar のLTable[]内でのインデックス
        i = i + 3
    return ret

###############################################################################
#　　各関数内のローカル変数（引数を含む）のサイズ計をlocalVarSize[]に求める             #
#　　関数番号は関数でない部分が fnno = 0、他は定義されている順に 1,2,3,……              #
#　　localVarSize[0]にはどの関数にも属していない(fnno = 0)ローカル変数の数、          #
#　　localVarSize[1]には fnno = 1 の関数にも属しているローカル変数の数、             #
#　　localVarSize[2]には fnno = 2 の関数にも属しているローカル変数の数、             #
#　　LTable[i].dmmaddr には LTable[i - 1] までの変数の数が入る                    #
#　　LTable[i].len にはその変数の個数が入っている 単純な変数なら1（配列ならその個数）    #
#   (Dmem[GVARSIZE + dmmaddr + baseReg] に LTable[i] の変数の値が入る)          #
#   配列でないなら、変数ｘの値が入る                                              #
#　（配列ならここから順にx[0], x[1], x[2], ……が入る）                             #
##############################################################################

def getLocalVarSize() :
    global localVarSize
    fnnoMax = 0
    localVarSize = []
    for i in range(len(LTable)) : #最大のfnnoを求める
        if LTable[i].fnno > fnnoMax :
            fnnoMax = LTable[i].fnno
    for i in range(fnnoMax + 1) :
        localVarSize.append(0) #関数の個数分、初期化
    for i in range(len(LTable)) :
        ln = LTable[i].len
        fnno = LTable[i].fnno
        LTable[i].dmmaddr = localVarSize[fnno]
        localVarSize[fnno] = localVarSize[fnno] + ln

#########################################
#   関数の開始行を与えて終了行を求める      　#
#   funcAddrListの[start, ＿]を探す     　#
#########################################

def searchFuncAddr(start) :
    for i in range(len(funcAddrList)) :
        x = funcAddrList[i]
        if x[0] == start :
            return x[1]
    return -1

###########################################################################
#   InterCodeを走査して、while, for, if, elif, elseの次に必要なアドレスを入れる  #
###########################################################################

def setStartEndAddr() :
    stk = Stack()
    for i in range(len(InterCode)) :
        cm = InterCode[i][0]
        if cm == While or cm == For or cm == If or cm == Func :
            stk.push(i) #行番号をプッシュ
        elif cm == Elif or cm == Else :
            j = stk.pop()
            InterCode[j][1] = i
            stk.push(i)
        elif cm == End :
            j = stk.pop()
            InterCode[j][1] = i


def setIfAddr1(i) :
    ln = i
    while InterCode[ln][0] != End :
        ln = InterCode[ln][1]
    endAddr = ln #ここまで来たらlnはEndのアドレス
    ln = i
    while InterCode[ln][0] != End :
        #if, elif, else の行にendのアドレスを埋め込む
        InterCode[ln][2] = endAddr
        ln = InterCode[ln][1] #次のelif, else, endのアドレス

#if, elif, else の後にジャンプ先アドレスを埋め込む
def setIfAddr() :
    for i in range(len(InterCode)) :
        cm = InterCode[i][0]
        if cm == If :
            setIfAddr1(i)

def setBreakAddr() :
    global breakList
    breakList = []
    i = 0
    while i < len(InterCode) :
        ic = lookIc(i, 0)
        if ic == While or ic == For :
            i = setBreakAddr1(i)
        i += 1

######################################################################
#   Breakの次にそのbreak文が含まれるwhileブロックなどのendの行番号を書き込む  #
#   lineは見つかったwhile, forの行番号                                  #
#   最初のwhileやforに対応するendの行番号が返る                           #
######################################################################

def setBreakAddr1(line) :
    global breakList
    stk = Stack()
    i = line + 1
    while True :
        ic = lookIc(i, 0)
        if ic == While or ic == For :
            i = setBreakAddr1(i)
        elif ic == Break :
            stk.push(i) #breakの行番号をプッシュ
            breakList.append(i)
        elif ic == End and not (i in ifEndList) :
        #ifに対応するend以外のendなら
            for j in range(stk.size()) :
                #endの行番号をbreakの後ろに書き込み
                InterCode[stk.pop()][1] = i
            return i #end文の行番号を返す
        i += 1

############################################
#   return, break文の位置が正しいかチェック  　#
###########################################

def returnBreakChk() :
    for i in range(len(InterCode)) :
        ic = lookIc(i, 0)
        if ic == Return : #どれかの関数内にあるならok
            if fnnoList[i] == 0 :
                raise Exception(errmsg0 + str(i + 1))
        elif ic == Break :
            if i not in breakList :
                raise Exception(errmsg0 + str(i + 1))

def posChk() :
    global _line, ifEndList
    _line = 0
    ifEndList = []
    while _line < len(InterCode) :
        ic = InterCode[_line][0]
        if ic == While or ic == For :
            chkBlock()
        elif ic == Func :
            chkFuncBlock()
        elif ic == If :
            chkIfBlock()
        elif ic == Elif or ic == Else or ic == End :
            raise Exception(errmsg0 + str(_line + 1))
        _line += 1

##########################
#   ifを読んだらコールする 　#
##########################

def chkIfBlock() :
    global _line, ifEndList
    elseFlag = 0
    ln = _line
    _line += 1
    while _line < len(InterCode) :
        ic = InterCode[_line][0]
        if ic == While or ic == For :
            chkBlock()
        elif ic == If:
            chkIfBlock()
        elif ic == Else or ic == Elif :
            if elseFlag == 1:
                raise Exception(errmsg0 + str(_line + 1))
            if ic == Else:
                elseFlag = 1
        elif ic == Func:
            raise Exception(errmsg0 + str(_line + 1))
        elif ic == End: #if文に対応するend文
            ifEndList.append(_line) #end文の行番号を追加
            return
        _line += 1
    #endがないときここへ来る
    raise Exception(errmsg0 + str(ln + 1))

###############################################
#      while, for, funcを読んだらコールする      #
###############################################

def chkBlock() :
    global _line
    ln = _line
    _line += 1
    while _line < len(InterCode) :
        ic = InterCode[_line][0]
        if ic == While or ic == For :
            chkBlock()
        elif ic == If :
            chkIfBlock()
        elif ic == End :
            return
        elif ic == Elif or ic == Else or ic == Func:
            raise Exception(errmsg0 + str(_line + 1))
        _line += 1
    raise Exception(errmsg0 + str(ln + 1))

#######################################
#       funcを読んだらコールする         #
#######################################

def chkFuncBlock() :
    global _line
    ln = _line
    _line += 1
    while _line < len(InterCode) :
        ic = InterCode[_line][0]
        if ic == While or ic == For :
            chkBlock()
        elif ic == If:
            chkIfBlock()
        elif ic == End :
            return
        elif ic == Elif or ic == Else or ic == Func:
            raise Exception(errmsg0 + str(_line + 1))
        _line += 1
    raise Exception(errmsg0 + str(ln + 1))

#######################################
#    DblNum は読んである状態でコール      #
#######################################

def pushVal() : #変数から値を取り出してプッシュ
    no = nextic()
    v = VTable[no].val
    opstack.push(v)
    return

#####################################
#    行内のポインタを1だけ戻す     #
#####################################

def backlpt1() :
    global _lpt
    _lpt -= 1
    return

#######################################################
#   _lptが中間コードの対象の行の最後に達していなければ1戻す 　 #
#   最後に達したら戻さない                                #
#######################################################

def backlpt() :
    global _lpt
    if _lpt < len(InterCode[_line]) :
        _lpt -= 1
    return

#############################
#   _line, _lpt をセット     #
#############################

def setlpt2(line, lpt) :
    global _line, _lpt
    _line = line
    _lpt = lpt
    return

#####################
#   _line を1進める  #
#####################

def incLine() :
    setlpt2(_line + 1, 0)

#---------------------------
#次の中間コードを得る
#行の最後に到達していたら -1 が返る
#
def nextic():
    global _lpt
    if _lpt >= len(InterCode[_line]):
        return -1
    ic = InterCode[_line][_lpt]
    _lpt += 1
    return int(ic)
#---------------------------
#次の中間コードが ic であることを確認。一致すれば True。
#
def checkic(ic):
    if nextic() == ic:
        return True
    return False

#############################
#    InterCode[i][j]を得る   #
#############################

def lookIc(i, j) :
    return InterCode[i][j]

#############################################
#   !, +, - (ファクターの前につく記号)は最優先   #
#   例 ) !8 + 9 = 10                        #
#   factorを評価してopstakにプッシュ           #
#   文法チェック中には1がプッシュされて返る       #
#   _chkMode = 1 のときは文法チェック中        #
#   _chkMode = 0 のときは通常の実行中          #
#############################################

def factor() :
    if _chkMode == 1 :
    #■■■このブロックは文法チェック中に実行される
        ic = nextic()
        if ic == -1 : #行末だったらエラー
            raise Exception(errmsg0 + str(_line + 1))
        elif ic == Not or ic == Plus or ic == Minus :
            factor()
            x = opstack.pop()
            opstack.push(1)
            return
        elif ic == LParen :
            expression()
            if checkic(RParen) :
                return
            raise Exception(errmsg0 + str(_line + 1))
        elif ic == Lvar :
            x = getLvar()
            opstack.push(1)
            return
        elif ic == Gvar :
            x = getGvar()
            opstack.push(1)
            return
        elif ic == Dvar : #99
            x = getDvar()
            opstack.push(1)
            return
        elif ic == DblNum :
            opstack.push(1)
            ic = nextic()
            return
        elif ic == Fcall : #関数呼び出しはファクター
            synChkFcall()
            #文法チェック中には実際には関数コールはしないので
            #適当な戻り値をプッシュしておく
            opstack.push(1)
        elif ic == Toint or\
                    ic == Sin or ic == Cos or ic == Tan or\
                    ic == Dsin or ic == Dcos or ic == Dtan:
            #(式)を評価。文法チェック中は1をプッシュし、ポインタを進めるだけ。
            parenExp()
            return
        else :
            raise Exception(errmsg0 + str(_line + 1))
    else :
    #■■■このブロックは通常の実行用
        ic = nextic()
        if ic == -1 : #行末だったらエラー
            raise Exception(errmsg0 + str(_line + 1))
        elif ic == Not :
            factor()
            x = opstack.pop()
            if x == 0 :
                opstack.push(1)
            else :
                opstack.push(0)
        elif ic == Plus or ic == Minus :
            factor()
            x = opstack.pop()
            if ic == Minus :
                opstack.push(-x)
            else :
                opstack.push(x)
        elif ic == LParen :
            expression()
            ic = nextic() #RParenのはず
            return
        elif ic == Lvar :
            x = getLvar()
            opstack.push(x)
            return
        elif ic == Gvar :
            x = getGvar()
            opstack.push(x)
            return
        elif ic == Dvar :
            x = getDvar()
            opstack.push(x)
            return
        elif ic == DblNum :
            pushVal()
            return
        elif ic == Fcall : #関数呼び出しはファクター
            opstack.push(callFunc())
            return
        elif ic == Toint :
            parenExp() #(式)を評価
            opstack.push(int(opstack.pop()))
            return
        elif ic == Sin :
            parenExp()
            opstack.push(math.sin(opstack.pop()))
            return
        elif ic == Cos :
            parenExp()
            opstack.push(math.cos(opstack.pop()))
            return
        elif ic == Tan :
            parenExp()
            opstack.push(math.tan(opstack.pop()))
            return
        elif ic == Dsin :
            parenExp()
            opstack.push(math.sin(opstack.pop() * math.pi / 180))
            return
        elif ic == Dcos :
            parenExp()
            opstack.push(math.cos(opstack.pop() * math.pi / 180))
            return
        elif ic == Dtan :
            parenExp()
            opstack.push(math.tan(opstack.pop() * math.pi / 180))
            return
    return

##############################################
#   term(項)の評価。結果はopstackにプッシュされる　#
##############################################

def term() :
    factor()
    x = opstack.pop()
    opstack.push(x)
    ic = nextic()
    if ic == -1 : #続きがなければreturn
        return
    while ic == Mult or ic == Div\
                or ic == IDiv or ic == Mod or ic == Pow :
        factor()
        x = opstack.pop()
        y = opstack.pop()
        if ic == Mult :
            opstack.push(y*x)
        elif ic == Div :
            opstack.push(y/x)
        elif ic == IDiv :
            opstack.push(int(y//x))
        elif ic == Mod :
            opstack.push(int(y%x))
        else : #ic == Pow
            opstack.push(pow(y, x))
        ic = nextic()
        if ic == -1 :
            return
    backlpt1()
    return

###################################################
#   通常の式（4則、変数、関数などが混ざってもよい）の評価  #
#   結果はopstackにプッシュされる                     #
###################################################

def expressionB() :
    term()
    ic = nextic()
    if ic == -1 :
        return
    while ic == Plus or ic == Minus :
        term()
        x = opstack.pop()
        y = opstack.pop()
        if ic == Plus :
            opstack.push(y+x)
        else : #ic == Minus
            opstack.push(y-x)
        ic = nextic()
        if ic == -1 :
            return
    backlpt1()
    return

##################################################################
#   <, >, <=, >=, ==, != の混ざった式の評価 式の左から順に評価される    #
#   例えば 「x <= y > z == w」 だと x <= y の値 s を求め、       　　 #
#   s > z の値 t を求め、t == w の値を求める                   　 　　#
##################################################################

def expressionA() :
    expressionB() #左のデータをプッシュ
    ic = nextic()
    if ic == -1 :
        return
    while ic == Less or ic == LessEq or ic == Great \
                    or ic == GreatEq or ic == Equal or ic == NotEq :
        expressionB() #右のデータをプッシュ
        x = opstack.pop() #右
        y = opstack.pop() #左
        if ic == Less :
            opstack.push(y < x)
        elif ic == LessEq :
            opstack.push(y <= x)
        elif ic == Great :
            opstack.push(y > x)
        elif ic == GreatEq :
            opstack.push(y >= x)
        elif ic == Equal :
            opstack.push(y == x)
        elif ic == NotEq :
            opstack.push(y != x)
        ic = nextic()
        if ic == -1 :
            return
    backlpt1()
    return

############################################################
#   and, or の処理 式の評価はこのコールで始める            　    #
#   expressionA()と同様、先頭から順に値を求めていく            　#
#　　これから評価しようとしてる式の先頭を _lpt が指した状態でコール  #
#　　結果は opstack にプッシュされて返る                        #
#　　_lptが式の最後の次を指した状態で終了                        #
############################################################

def expression() :
    expressionA()
    ic = nextic()
    if ic == -1 :
        return
    while ic == And or ic == Or :
        expressionA()
        x = opstack.pop()
        y = opstack.pop()
        if ic == And :
            if y and x : 
                opstack.push(1)
            else :
                opstack.push(0)
        else : #ic == Or
            if y or x: 
                opstack.push(1)
            else :
                opstack.push(0)
        ic = nextic()
        if ic == -1 :
            return
    backlpt1()
    return
#------------------------------------------
def pushCallPara() :
    callParaList.append(baseReg)
    callParaList.append(spReg)
    callParaList.append(_line)
    callParaList.append(_lpt)
    callParaList.append(_fnno)
#------------------------------------------
def popCallPara() :
    global baseReg, spReg, _line, _lpt, _fnno
    _fnno = callParaList.pop()
    _lpt = callParaList.pop()
    _line = callParaList.pop()
    spReg = callParaList.pop()
    baseReg = callParaList.pop()

############################################
#   関数呼び出しコード（Fcall）を読んでから呼ぶ  #
#   関数をコールして値を得る                　 #
############################################

def callFunc() :
    global baseReg, spReg, _lpt, _fnno
    global fEnd, fReturn
    argStack = Stack() 
    argStack1 = Stack() 
    j = nextic() #Fcallの次には関数のインデックスが埋め込まれている
    argList = FTable[j].argList
    if not checkic(LParen) :
        return False
    if len(argList) == 0 :
        if not checkic(RParen) :
            return False
    for i in range(len(argList)) : #コールされた関数に引数をセット
        expression()
        x = opstack.pop()
        argStack.push(x)
        if i == len(argList) - 1 :
            ic = nextic()
            if ic != RParen :
                return False
        else:
            if not checkic(Comma) :
                return False
    #ここまでで引数がargStackにセットされている
    _fnno = FTable[j].fnno
    pushCallPara()
    fstart = FTable[j].line
    setlpt2(fstart + 1, 0)
    baseReg = spReg
    spReg = baseReg + localVarSize[FTable[j].fnno]
    for i in range(argStack.size()) :
        argStack1.push(argStack.pop()) #引数の順を逆転させる
    #関数に引数を渡す
    for i in range(len(argList)) :
        x = argStack1.pop()
        setLvar2(argList[i], x)
    execBlock() #このブロックで読んだreturn, endは以降で処理
    if fReturn == 1 :  #return はここで処理
        fReturn = 0 #フラグをクリア
        ic = nextic()
        if ic == -1 : #戻り値なしのreturnだった
            popCallPara()
            return 1 #戻り値なしでも1を返す。
        _lpt -= 1 #ポインタを戻す
        expression() #戻り値を評価
        ret = opstack.pop()
        popCallPara()
        return ret
    elif fEnd == 1 : #関数の定義終了のendを読んだ
        fEnd = 0 #フラグをクリア
        popCallPara()
        return 1 #returnなしの関数は1を返す。
    return 0 #上位の関数には何も伝えない

###################################################
#   LTable[i]が指定する変数にｘを代入する          　  #
#   baseReg, GVARSIZEに必要な値を入れておく必要がある 　#
#   (Dmemにｘを格納する)                         　  #
###################################################

def setLvar2(i, x) :
    Dmem[LTable[i].dmmaddr + GVARSIZE + baseReg] = x

#######################################
#   ローカル変数の値を取得              　#
#   行先頭の Lvar を読んだ状態でコール   　#
#######################################

def getLvar() :
    no = nextic()
    dmmaddr = LTable[no].dmmaddr
    v = Dmem[GVARSIZE + dmmaddr + baseReg]
    return v