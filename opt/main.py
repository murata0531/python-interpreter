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

##############################
# 各種ファイルのインポート
##############################




##############################
#      メイン
##############################

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
