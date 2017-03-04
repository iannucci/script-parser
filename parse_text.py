#!/usr/bin/env python

# MIT License

# Copyright (c) 2017 Bob Iannucci

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pyparsing import *

# pyparsing docs:
#   https://pythonhosted.org/pyparsing/

# The grammar contained here ascribes to the NARRATOR all text in square brackets [...]

a = None  

emdash_suppress = Suppress("--")
performer_name = oneOf( 'SCENE JOHNNY FIRST_LONGSHOREMAN \
                         SECOND_LONGSHOREMAN THE_POSTMAN \
                         LARRY CHRIS MARTHY ANNA THE_VOICE \
                         BURKE JOHNSON NARRATOR' )('performer_name')
begin_performer = performer_name + emdash_suppress

roman_numerals = Word('IVLXCDMivlxcdm')
act_number = roman_numerals
begin_act = Keyword('ACT') + act_number

simple_word = Word( alphas )
contraction_pieces = simple_word + "\'" + Optional(simple_word)
contraction_word = Combine(contraction_pieces)

leading_contraction_pieces = "\'" + simple_word
leading_contraction_word = Combine(leading_contraction_pieces)

hyphen_suppress = Suppress("-")
hyphenated_pieces = simple_word + hyphen_suppress + simple_word
hyphenated_word = Combine(hyphenated_pieces)
script_word = MatchFirst([hyphenated_word, contraction_word, leading_contraction_word, performer_name, simple_word])

simple_or_contracted_word = Or([contraction_word, simple_word])
three_hyphenated_words = simple_or_contracted_word + hyphen_suppress + simple_or_contracted_word + hyphen_suppress + simple_or_contracted_word

four_hyphenated_words = simple_or_contracted_word + hyphen_suppress + simple_or_contracted_word + hyphen_suppress + simple_or_contracted_word + hyphen_suppress + simple_or_contracted_word

emdash_joined_words = script_word + emdash_suppress + script_word
# Or will parse the LONGEST match
#
# Note the use of NotAny here -- these stop the parser in its tracks when there 
# is a break in performer or change-of-act
actor_words =  NotAny(begin_performer) + NotAny(begin_act) + Or([four_hyphenated_words, three_hyphenated_words, emdash_joined_words, script_word])
actor_phrase = OneOrMore(actor_words)('actor_phrase')
open_bracket_suppress = Suppress("[")
close_bracket_suppress = Suppress("]")
narrator_phrase = open_bracket_suppress + OneOrMore(actor_words)('narrator_phrase') + close_bracket_suppress
script_phrase = Group(Or([narrator_phrase, actor_phrase]))

all_phrases = OneOrMore(script_phrase)('phrases')
script_line = Group(begin_performer + all_phrases)

all_lines = OneOrMore(script_line)('script_lines')

script_act = Group(begin_act + all_lines)
script = OneOrMore(script_act)('acts')

# -------------------------------------------------------------------------------

def get_script_text(file_name='script.txt'):
    with open(file_name, 'r') as myfile:
        data = myfile.read().lstrip("\xef\xbb\xbf").strip().replace('\n', ' ').replace('\r', '').translate(None, '().,?!;:')
    return data
                    
def count(file_name='script.txt'):
    '''
    Count the words for each character in a script
    '''
    performers = dict( SCENE=0, JOHNNY=0, FIRST_LONGSHOREMAN=0, SECOND_LONGSHOREMAN=0, THE_POSTMAN=0, \
    LARRY=0, CHRIS=0, MARTHY=0, ANNA=0, THE_VOICE=0, BURKE=0, JOHNSON=0, NARRATOR=0)
        
    t = get_script_text(file_name)

    try:
        p = script.parseString(t)
        
    # See http://pyparsing.wikispaces.com/share/view/30875955#30901387
    except ParseException, err:
        prefix_length = 20
        suffix_length = 20
        begin = max(0,err.column - prefix_length)
        end = min(len(t), err.column + suffix_length)
        print '...' + err.line[begin:end] + '...'
        print '   ' + " "*(err.column - begin - 1) + "^"
        print "ParseError: " + err.msg.split('\n', 1)[0]
        return
        
    print "Number of acts: %d" % (len(p['acts']), )
        
    for act in p['acts']:
        print act
        for script_line in act['script_lines']:
            name = script_line['performer_name']
            for phrase in script_line['phrases']:
                try:
                    np = phrase['narrator_phrase']
                    performers['NARRATOR'] += len(np)
                    # print phrase
                except:
                    performers[name] += len(phrase)
                    # if name == 'SCENE':
                    #    print phrase
    return performers  
    
def test():
    '''
    Run simple testcases to check that basic parsing of lines, acts and scripts are parsed properly.
    '''

    try:
        t = 'FIRST_LONGSHOREMAN--Gimme a scoop this time [he said]'
        print "Parsing " + t
        p = script_line.parseString(t)
        print "%s\n" % (p, )
        assert p[0]['performer_name'] == 'FIRST_LONGSHOREMAN'
        assert len(p[0]['phrases']) == 2

        t = 'ACT I FIRST_LONGSHOREMAN--Gimme a scoop this time SECOND_LONGSHOREMAN--Yo [The Curtain Falls]'
        print "Parsing " + t
        p = script_act.parseString(t)
        print "%s\n" % (p, )
        assert len(p[0]['script_lines']) == 2
        
        t = 'ACT I FIRST_LONGSHOREMAN--Help [The Curtain Falls] ACT II SECOND_LONGSHOREMAN--Hello [The Curtain Falls]'
        print "Parsing " + t
        p = script.parseString(t)
        print "%s\n" % (p, )
        assert len(p['acts']) == 2
        
    except ParseException, err:
        prefix_length = 20
        suffix_length = 20
        begin = max(0,err.column - prefix_length)
        end = min(len(t), err.column + suffix_length)
        print '...' + err.line[begin:end] + '...'
        print '   ' + " "*(err.column - begin - 1) + "^"
        print "ParseError: " + err.msg.split('\n', 1)[0]
        return
