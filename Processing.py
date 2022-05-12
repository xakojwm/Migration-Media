from google.cloud import language_v1
import os
from striprtf.striprtf import rtf_to_text
import pandas as pd
import pickle

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.curdir, 'client_secret.json')

def sample_analyze_sentiment(text_content):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}
    encoding_type = language_v1.EncodingType.UTF8
    response1 = client.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})
    response2 = client.analyze_entities(request={'document': document, 'encoding_type': encoding_type})
    return response1.document_sentiment.score, response1.document_sentiment.magnitude, response2.entities

file_paths = ['Sample (Download as RTF) /.DS_Store', 'Sample (Download as RTF) /Midwest/.DS_Store', 'Sample (Download as RTF) /Midwest/St. Louis Post-Dispatch/immigrant_ AND _Mexico_ AND _border_ St. Louis Post-Dispatch.xlsx', 'Sample (Download as RTF) /Midwest/St. Louis Post-Dispatch/ _illegal immigrant_ st louis.rtf', 'Sample (Download as RTF) /Midwest/The Capital Times _ Wisconsin State Journal/border_ AND _Mexico_ AND _immigrant_ - Capital Times _ Wisconsin State Journal.xlsx', 'Sample (Download as RTF) /Midwest/The Capital Times _ Wisconsin State Journal/_illegal immigrant_ - Capital Times _ Wisconsin State Journal.rtf', 'Sample (Download as RTF) /NYT/NYT 4.rtf', 'Sample (Download as RTF) /NYT/NYT 3.rtf', 'Sample (Download as RTF) /NYT/NYT 2.rtf', 'Sample (Download as RTF) /NYT/NYT1.rtf', 'Sample (Download as RTF) /NYT/NYT5.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1406.rtf', 'Sample (Download as RTF) /South/Washington Post/first 100.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1410.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1406.rtf.docx', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1502.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1449.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1446.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1426.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1430.rtf', 'Sample (Download as RTF) /South/Washington Post/Factiva-20220403-1435.rtf', 'Sample (Download as RTF) /West/.DS_Store', 'Sample (Download as RTF) /West/Arizona Daily Star/Arizona Daily Star (illegal immigrant) 2.rtf', 'Sample (Download as RTF) /West/Arizona Daily Star/Arizona Daily Star(illegal immigrant).rtf', 'Sample (Download as RTF) /AP News /15.rtf', 'Sample (Download as RTF) /AP News /14.rtf', 'Sample (Download as RTF) /AP News /16.rtf', 'Sample (Download as RTF) /AP News /17.rtf', 'Sample (Download as RTF) /AP News /13.rtf', 'Sample (Download as RTF) /AP News /10.rtf', 'Sample (Download as RTF) /AP News /11.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP 6.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP 7.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP news 1.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP 5.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP news 2.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP 10.rtf', 'Sample (Download as RTF) /AP News /Factiva AP 8.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP 3.rtf', 'Sample (Download as RTF) /AP News /Factiva AP 4.rtf', 'Sample (Download as RTF) /AP News /Factiva-AP 9.rtf', 'Sample (Download as RTF) /AP News /20.rtf', 'Sample (Download as RTF) /AP News /19.rtf', 'Sample (Download as RTF) /AP News /18.rtf', 'Sample (Download as RTF) /Northeast/New York Daily News/NY daily news.rtf', 'Sample (Download as RTF) /Northeast/The Boston Globe/Boston Globe.rtf', 'Sample (Download as RTF) /Northeast/The Boston Globe/boston globe 2.rtf']
used_paths = ['Sample (Download as RTF) /Midwest/St. Louis Post-Dispatch/ _illegal immigrant_ st louis.rtf',
              'Sample (Download as RTF) /Midwest/The Capital Times _ Wisconsin State Journal/_illegal immigrant_ - Capital Times _ Wisconsin State Journal.rtf']


def file_name_encoding():
    file_code = {}
    count = 0
    code = []
    f = []
    for p in file_paths:
        file_code[p] = count
        file_code[count] = p
        count += 1
    for key in file_code:
        if type(key) == int:
            code.append(key)
            f.append(file_code[key])
    return code, f


def getArticles(test):
    """
    takes a rtf file from factiva and splits into list of txt articles
    """
    f = open(test, 'r')
    file_text = rtf_to_text(f.read())
    article_list = []
    start = 0
    count = 0
    i = 0
    while i < len(file_text) - 11:
        if file_text[i: i + 11] == "\n\nDocument ":
            article_list.append(file_text[start:i])
            j = i + 11
            while file_text[j] != ' ':
                j += 1
            i = j
            start = i
            count += 1
        i += 1
    return article_list

def process():
    headers_art = ['code from sheet', 'file it represents']
    file_code, f = file_name_encoding()
    df = pd.DataFrame(columns=headers_art)
    df['code from sheet'] = file_code
    df['file it represents'] = f


    df.to_csv('articlecodes.csv')

    headers = ['sentiment score', 'sentiment magnitude']

    for path in file_paths:
        df = pd.DataFrame(columns=headers)
        try:
            print()
            print("trying " + path)
            print()

            if path[len(path) - 4:] == '.rtf' and path not in used_paths:
                articleList = getArticles(path)
                print(len(articleList))
                allEntities = []
                score_list = []
                magnitude_list = []
                for article in articleList:
                    score, magnitude, entities = sample_analyze_sentiment(article)
                    ent_temp = []
                    score_list.append(score)
                    magnitude_list.append(magnitude)
                    allEntities.append(ent_temp)

                df['sentiment score'] = score_list
                df['sentiment magnitude'] = magnitude_list
                df.to_csv('Sentiment_for_' + str(file_code[path]) + '.csv')

                fileobj = open('Entities_for' + str(file_code[path]) + '.txt', 'wb')
                pickle.dump(allEntities, fileobj)
                fileobj.close()

        except Exception as e:
            print('error occurs here:')
            print(e)
            print(path)
            print()

def entity_getter(text_content):
    """
    exclusively for getting entities
    """
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT

    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response2 = client.analyze_entities(request={'document': document, 'encoding_type': encoding_type})
    e = response2.entities
    return e



