import json
import time
import string
import math
from konlpy.tag import Okt
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
        self.wvById = []
        self.rankedID = []
        for termItem in self.terms:
            self.termDataDict[termItem] = TermData(termItem)

    def calWeightVector(self, table):
        for idWeight in table:
            isInFlag = False
            for rawWV in self.wvById:
                if idWeight[0] in rawWV:
                    rawWV[1] += pow(idWeight[1], 2)
                    isInFlag = True
            if not isInFlag:
                self.wvById.append([idWeight[0], pow(idWeight[1], 2)])

    def calRank(self):
        for wvPair in self.wvById:
            wvPair[1] = math.sqrt(wvPair[1])
        self.wvById.sort(key=lambda x: -x[1])
        for wvPair in self.wvById:
            self.rankedID.append(wvPair[0])


class InvIndex:  # inverted index 자료구조
    def __init__(self):
        self.numOfTerms = -1
        self.myTermNode = dict()

    def getTfIdfTable(self, term):
        table = []
        for docID in self.myTermNode[term].myDocTFDict.keys():
            table.append((docID, self.getTf(term, docID) * self.getIdf(term)))
        table.sort(key=lambda x: -x[1])
        return table

    def getTf(self, term, docID):
        if docID not in self.myTermNode[term].myDocTFDict:
            return 0
        return math.log10(1 + self.myTermNode[term].myDocTFDict[docID])

    def getIdf(self, term):
        return math.log10(self.myTermNode[term].idf)

    def addTitleTerm(self, term, docId):
        if term in self.myTermNode:
            rootTN = self.myTermNode[term]
            curTN = rootTN.tail
            curDocId = curTN.docId
            if curDocId == docId:
                if docId in rootTN.myDocTFDict:
                    rootTN.myDocTFDict[docId] += 100
                else:
                    rootTN.myDocTFDict[docId] = 100
                return
            rootTN.freq += 1
            curTN.nxt.append(Node(docId))
            rootTN.tail = curTN.nxt[0]
        else:
            self.myTermNode[term] = TermNode(term, docId)
            self.myTermNode[term].myDocTFDict[docId] = 1

    def addTerm(self, term, docId):
        if term in self.myTermNode:
            rootTN = self.myTermNode[term]
            curTN = rootTN.tail
            curDocId = curTN.docId
            if curDocId == docId:
                if docId in rootTN.myDocTFDict:
                    rootTN.myDocTFDict[docId] += 1
                else:
                    rootTN.myDocTFDict[docId] = 1
                return
            rootTN.freq += 1
            curTN.nxt.append(Node(docId))
            rootTN.tail = curTN.nxt[0]
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
        self.tail = self.nxt[0]


class Node:  # 시작 노드에 덧붙이는 노드들
    def __init__(self, docId):
        self.docId = docId
        self.nxt = []


def calPathByDocID(docID):
    path = rootPath
    position = calPosByDocID(docID)
    # 100 단위로 AA AB AC 나뉨
    # 1 단위로 wiki_00 wiki_01 wiki_03 나뉨
    dirPos = int(position / 100)
    filePos = position % 100
    if dirPos == 0:
        path += 'AA'
    if dirPos == 1:
        path += 'AB'
    if dirPos == 2:
        path += 'AC'
    if dirPos == 3:
        path += 'AD'
    if dirPos == 4:
        path += 'AE'
    if dirPos == 5:
        path += 'AF'
    if dirPos == 6:
        path += 'AG'
    if dirPos == 7:
        path += 'AH'
    if filePos < 10:
        path += '\\wiki_0' + str(filePos)
    else:
        path += '\\wiki_' + str(filePos)
    return path


def calPosByDocID(docID):
    index = 0
    intDocID = int(docID)
    for lastDocID in lastID:
        if intDocID <= lastDocID:
            return index
        index += 1


cnt = 0
konlpy = Okt()
invIndex = InvIndex()
lastID = []

''' ------------ file 읽어와서 처리 -------------- '''


def loadFileToInvInd(path):
    global konlpy
    global invIndex
    global lastID

    try:
        with open(path, encoding='UTF8') as f:
            for line in f:
                data = json.loads(line)
                print('<id:%s> 에서 문서 로드 중...' % data['id'])
                curString = data['title']
                titleNounData = konlpy.nouns(curString)
                for textItem in titleNounData:
                    invIndex.addTitleTerm(textItem, data['id'])
                curString = data['text']
                nounData = konlpy.nouns(curString)
                for textItem in nounData:
                    invIndex.addTerm(textItem, data['id'])
        lastID.append(int(data['id']))

    except FileNotFoundError:
        print("there is no file: %s" % path)


def loadFileToEmbed(path, docId):
    try:
        with open(path, encoding='UTF8') as f:
            for line in f:
                data = json.loads(line)
                if docId != data['id']:
                    continue
                if len(data['text']) < 100:
                    embed = discord.Embed(title=data['title'], description=data['text'], color=0x00ff56)
                else:
                    embed = discord.Embed(title=data['title'], description=data['text'][:100] + '...', color=0x00ff56)
                embed.add_field(name='url', value=data['url'], inline=False)
                return embed

    except FileNotFoundError:
        print("there is no file: %s" % path)


''' -----------------------메인 코드 실행부-------------------------- '''

global rootPath
rootPath = '.\corpus\\'
letters = list(string.ascii_uppercase)
letters.extend([i + b for i in letters for b in letters])

cur = rootPath
# for item in letters:   # 전체일때
for item in {'AA'}:  # AA폴더 안에만
    if len(item) < 2:
        continue
    if item == 'AI':
        break
    dirPath = rootPath + item + '\wiki_'
    # for num in range(100): # 전체일때
    for num in range(3):  # wiki_00, wiki_01 만
        if item == 'AH' and num > 6:
            break
        if num < 10:
            cur = dirPath + '0' + str(num)
        else:
            cur = dirPath + str(num)

        print('%s 파일 로드중...' % cur)
        loadFileToInvInd(cur)

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
    if message.content.startswith('!!검색'):
        start = time.time()
        query = message.content[4:]
        if len(query) == 0:
            await message.channel.send('검색어를 입력하세요...')
            return
        await message.channel.send('검색어: %s' % query)

        qIdDict[message.id] = qData(query)
        curQD = qIdDict[message.id]
        for term in curQD.terms:
            TD = curQD.termDataDict[term]
            curQD.calWeightVector(TD.weightTable)
            await message.channel.send(term)
        curQD.calRank()
        cnt = 0
        for docID in curQD.rankedID:
            embed = loadFileToEmbed(calPathByDocID(docID), docID)
            await message.channel.send(embed=embed)
            cnt += 1
            if cnt == 10:
                break
        await message.channel.send('걸린 시간: '+str(time.time()-start)+'초')


client.run('NzcxMjM1NjY1NzM1ODQzODQw.X5pLLw.CdQpT-Mx96X0NxchT2mKFPGfutM')
