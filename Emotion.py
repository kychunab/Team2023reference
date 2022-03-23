# -*- coding:utf-8 -*-
import datetime
from cnsenti import Sentiment

from Config import *

# Statistical emotions
def StatisticalEmotions(dataset):
    map_emotion = {}
    senti = Sentiment()
    for one in dataset[1:]:
        try:
            result = senti.sentiment_count(one[ARRAYID['content']])
            map_emotion[one[ARRAYID['docid']]] = result
            # print(result)
        except Exception as e:
            result = {'words': 0, 'sentences': 0, 'pos': 0, 'neg': 0}
            map_emotion[one[ARRAYID['docid']]] = result

# Data display preservation
def saveToTxt(text, filename):
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(text)
        f.write("\n")

# Keyword extraction, and save
def extrectAnalysisKeyWords(emode, exdict, numn, remove_words, weight_enable):
    text = ""
    activen = 0
    while True:
        if activen >= numn:
            break
        max_key = max(exdict, key=exdict.get)
        max_value = exdict[max(exdict, key=exdict.get)]
        if max_key not in remove_words:
            activen += 1
            if weight_enable:
                text += " " + str(max_key) + ":" + str(max_value)
            else:
                text += " " + str(max_key)
            if emode == TIME_MODE and activen == 1:
                global INTERESTING_TEXT
                INTERESTING_TEXT += str(max_key) + " "
        exdict.pop(max_key)
    text += "\n"
    return text


# Traversing data for conditional analysis
def conditionAnalysis(dataset, nkey_array, mode):
    if mode:
        # Time analysis
        first_date, second_date = None, None
        dt = datetime.timedelta(days=TIME_INTERVAL)
        time_dict = {}
        # Emotion analysis
        emo_num_dict = {ZEROEQUNUM:0, EQUNUM:0, POSNUM:0, NEGNUM:0}
        emo_dict = {ZEROEQU: {}, EQU:{}, POS:{}, NEG:{}}

        # data loop
        for i in range(0, len(dataset)):
            # Time analysis
            if TIME_ANALYSIS in mode:
                now_date = dataset[i][ARRAYID['pubdate']]
                # Determine if it is a time type
                if isinstance(now_date, datetime.datetime):
                    if first_date is None:  # First time assignment
                        temp_date = str(now_date.year)+"-"+str(now_date.month)+"-"+str(now_date.day)
                        first_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")
                        second_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")+dt
                        # print(first_date, second_date)
                    # Determine time range
                    if first_date <= now_date <= second_date and i != len(dataset)-1:
                        for nk in range(0, EACH_LINE_KEYWORDS):
                            nkword = nkey_array[i][nk]
                            if nkword in time_dict:
                                time_dict[nkword] += 1
                            else:
                                time_dict[nkword] = 1
                            if nkword in INTERESTING_WORDS:
                                tt = str('keyward: '+str(nkword)+"\n"
                                         +now_date.strftime("%Y-%m-%d-%H:%M:%S")+"\n"
                                         +'positiveemo_count: '+str(dataset[i][ARRAYID['positiveemo_count']])+"\n"
                                         +'negativeemo_count: '+str(dataset[i][ARRAYID['negativeemo_count']])+"\n"
                                         +str(dataset[i][ARRAYID['content']].encode("gbk", 'ignore').decode("gbk", "ignore")).replace('\s+', '\\\\').replace('\n', '\\\\')+"\n")
                                saveToTxt(tt, INTERESTING_CONTENT_FILENAME)

                    else:
                        # Find weekly reviews
                        timetext = str(first_date.strftime("%Y-%m-%d-%H:%M:%S")) + "->" + str(second_date.strftime("%Y-%m-%d-%H:%M:%S"))
                        timetext += extrectAnalysisKeyWords(TIME_MODE, time_dict, EACH_WEEKEND_N, KEY_STOP_WORDS, ENABLE_TIME_WEIGHT)
                        saveToTxt(timetext, TIME_TXT_FILENAME)
                        time_dict = {}
                        first_date = second_date
                        second_date = second_date+dt

            # emotion trend analysis
            if EMOTION_ANALYSIS in mode:
                negativeemo_count = dataset[i][ARRAYID['negativeemo_count']]
                positiveemo_count = dataset[i][ARRAYID['positiveemo_count']]
                # Result counts
                if negativeemo_count > positiveemo_count:
                    emo_num_dict[NEGNUM] += 1
                elif negativeemo_count < positiveemo_count:
                    emo_num_dict[POSNUM] += 1
                elif negativeemo_count == positiveemo_count and positiveemo_count != 0:
                    emo_num_dict[EQUNUM] += 1
                elif negativeemo_count == positiveemo_count and positiveemo_count == 0:
                    emo_num_dict[ZEROEQUNUM] += 1

                # Keywords statistic
                for emonk in range(0, EMO_EACH_LINE):
                    emonkword = nkey_array[i][emonk]
                    if negativeemo_count > positiveemo_count:
                        if emonkword in emo_dict[NEG]:
                            emo_dict[NEG][emonkword] += 1
                        else:
                            emo_dict[NEG][emonkword] = 1
                    elif negativeemo_count < positiveemo_count:
                        if emonkword in emo_dict[POS]:
                            emo_dict[POS][emonkword] += 1
                        else:
                            emo_dict[POS][emonkword] = 1
                    elif negativeemo_count == positiveemo_count and positiveemo_count != 0:
                        if emonkword in emo_dict[EQU]:
                            emo_dict[EQU][emonkword] += 1
                        else:
                            emo_dict[EQU][emonkword] = 1
                    elif negativeemo_count == positiveemo_count and positiveemo_count == 0:
                        if emonkword in emo_dict[ZEROEQU]:
                            emo_dict[ZEROEQU][emonkword] += 1
                        else:
                            emo_dict[ZEROEQU][emonkword] = 1

                if i == len(dataset)-1:
                    emotext = str(emo_num_dict) + "\n\n"
                    for emok, emov in emo_dict.items():
                        emotext += str(emok) + " "
                        emotext += extrectAnalysisKeyWords(EMO_MODE, emov, EACH_EMO_N, KEY_STOP_WORDS, ENABLE_EMO_WEIGHT)
                        emotext += "\n"
                    saveToTxt(emotext, EMO_TXT_FILENAME)

            # Show progress of processing
            if i % 80000 == 0:
                print("\n{} / {}  ".format(i, len(dataset)), end="")
            if i % 1000 == 0:
                print("#", end="")