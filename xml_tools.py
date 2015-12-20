#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from lxml import etree, html
from html.parser import HTMLParser


def neat(text):
    text = text.replace('\n\n', '_zzz_')
    text = text.replace('\n', ' ')
    text = text.replace('_zzz_', '\n\n')
    return text


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def tournament_info(url):
    url += '/xml'
    tournament_url = urllib2.urlopen(url)
    tournament = etree.fromstring(tournament_url.read())
    tournament_url.close()
    result = dict()
    answer = tournament.find('Title').text
    answer += '\n' + tournament.find('PlayedAt').text
    if tournament.find('Editors').text is not None:
        answer += '\n' + u'Редакторы: ' + tournament.find('Editors').text
    if tournament.findtext('Info') is not None:
        answer += '\n' + neat(tournament.findtext('Info'))
    result['description'] = answer
    result['n_tours'] = tournament.findtext('ChildrenNum')
    result['n_questions'] = []
    result['tour_titles'] = []
    result['tour_info'] = []
    result['tour_editors'] = []
    for child in tournament:
        if child.tag == 'tour':
            result['n_questions'].append(int(child.findtext('QuestionsNum')))
            result['tour_titles'].append(child.findtext('Title'))
            result['tour_info'].append(neat(child.findtext('Info')))
            result['tour_editors'].append(child.findtext('Editors'))
    return result


def q_and_a(tournament, tour, question):
    url = 'http://db.chgk.info/question/{}.{}/{}/xml'.format(tournament.split('/')[-1], tour, question)
    question_url = urllib2.urlopen(url)
    quest = etree.fromstring(question_url.read())
    question_url.close()
    result = dict()
    result['question'] = neat(strip_tags(quest.findtext('Question')))
    result['answer'] = neat(strip_tags(quest.findtext('Answer')))
    if quest.findtext('Comments'):
        result['comments'] = neat(strip_tags(quest.findtext('Comments')))
    result['sources'] = neat(strip_tags(quest.findtext('Sources')))
    result['authors'] = strip_tags(quest.findtext('Authors'))
    xhtml = html.document_fromstring(quest.findtext('Question'))
    imageurl = xhtml.xpath('//img/@src')
    if len(imageurl) > 0:
        result['q_image'] = imageurl[0]
    return result

if __name__ == "__main__":
    print tournament_info("http://db.chgk.info/tour/balt16-2")['description']
    for item in q_and_a("http://db.chgk.info/tour/balt16-2", 1, 1).values():
        print item