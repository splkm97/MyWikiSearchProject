#-*- coding: utf-8 -*-
import json
import string
import math
from konlpy.tag import Mecab
import discord


class TermData:
    def __init__(self, term):
        self.term = term
        self.weightTable = invIndex.getTfIdfTable(term)


class qData:
    def __init__(self, query):
        curString = query
        self.query = query
        self.terms = konlpy.nouns(curString)
        self.termDataDict = dict()
        for termItem in self.terms:
            self.termDataDict[termItem] = TermData(termItem)


class InvIndex:  # inverted index 자료구조
    def __init__(self):
        self.numOfTerms = -1
        self.myTermNode = dict()

    def getTfIdfTable(self, term):
        table = []
        for docID in self.myTermNode[term].myDocTFDict.keys():
            table.append([docID, self.getTf(term, docID) * self.getIdf(term)])
        table.sort(key=lambda element: element[1])
        return table[:10]

    def getTf(self, term, docID):
        if docID not in self.myTermNode[term].myDocTFDict:
            return 0
        return math.log10(1 + self.myTermNode[term].myDocTFDict[docID])

    def getIdf(self, term):
        return math.log10(self.myTermNode[term].idf)

    def addTerm(self, term, docId):
        if term in self.myTermNode:
            curTN = self.myTermNode[term]
            rootTN = self.myTermNode[term]
            while len(curTN.nxt) != 0:
                curDocId = curTN.nxt[0].docId
                curTN = curTN.nxt[0]
            if curDocId == docId:
                if docId in rootTN.myDocTFDict:
                    rootTN.myDocTFDict[docId] += 1
                else:
                    rootTN.myDocTFDict[docId] = 1
                return
            rootTN.freq += 1
            curTN.nxt.append(Node(docId))
        else:
            self.myTermNode[term] = TermNode(term, docId)
            self.myTermNode[term].myDocTFDict[docId] = 1

    def calNumOfTerms(self):
        self.numOfTerms = len(self.myTermNode)

    def calIdf(self):
        self.calNumOfTerms()
        for curTN in self.myTermNode.values():
            curTN.idf = self.numOfTerms / curTN.freq


class TermNode:  # term 과 freq, docID 를 가지는 시작 노드
    def __init__(self, term, docId):
        self.term = term
        self.myDocTFDict = dict()
        self.freq = 1
        self.idf = -1.0
        self.nxt = []
        self.nxt.append(Node(docId))


class Node:  # 시작 노드에 덧붙이는 노드들
    def __init__(self, docId):
        self.docId = docId
        self.nxt = []


cnt = 0
konlpy = Mecab()
invIndex = InvIndex()

''' ------------ file 읽어와서 처리 -------------- '''


def loadfile(path):
    global konlpy
    global invIndex
    curString = u'현재 스트링'
    try:
        with open(path, encoding='UTF8') as f:
            for line in f:
                data = json.loads(line)
                print('<id:%s> 에서 문서 로드 중...' % data['id'])
                curString = data['title']
                titleNounData = konlpy.nouns(curString)
                for textItem in titleNounData:
                    invIndex.addTerm(textItem, data['id'])
                curString = data['text']
                nounData = konlpy.nouns(curString)
                for textItem in nounData:
                    invIndex.addTerm(textItem, data['id'])

    except FileNotFoundError:
        print("there is no file: %s" % cur)


''' -----------------------메인 코드 실행부-------------------------- '''

rootPath = '.\corpus\\'
letters = list(string.ascii_uppercase)
letters.extend([i + b for i in letters for b in letters])

# for item in letters:   # 전체일때
for item in {'AA'}:  # AA폴더 안에만
    if len(item) < 2:
        continue
    if item == 'AI':
        break
    dirPath = rootPath + item + '\wiki_'
    for num in range(100): # 전체일때
    #for num in range(1):  # wiki_00만
        if item == 'AH' and num > 6:
            break
        if num < 10:
            cur = dirPath + '0' + str(num)
        else:
            cur = dirPath + str(num)

        print('%s 파일 로드중...' % cur)
        loadfile(cur)

print('idf 값 계산중...')
invIndex.calIdf()
curID = "340"
wantStr = '일치'
print('<id:%s> 문서에서 \'%s\' 에 대한 tf값: ' % (curID, wantStr) + str(invIndex.getTf(wantStr, curID)))
print('%s 까지에서 \'%s\' 에 대한 freq값: ' % (cur, wantStr) + str(invIndex.myTermNode[wantStr].freq))
print('%s 까지에서 \'%s\' 에 대한 idf값: ' % (cur, wantStr) + str(invIndex.myTermNode[wantStr].idf))
print()

client = discord.Client()
global qIdDict
qIdDict = dict()


@client.event
async def on_ready():
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith('!검색'):
        query = message.content[3:]
        if len(query) == 0:
            await message.channel.send('검색어를 입력하세요...')
            return
        await message.channel.send('검색어: %s' % query)

        qIdDict[message.id] = qData(query)
        curQD = qIdDict[message.id]
        for term in curQD.terms:
            TD = curQD.termDataDict[term]
            print(TD.weightTable[:10])
            await message.channel.send(term)


client.run('NzcxMjM1NjY1NzM1ODQzODQw.X5pLLw.CdQpT-Mx96X0NxchT2mKFPGfutM')
