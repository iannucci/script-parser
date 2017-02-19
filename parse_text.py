from pyparsing import *

#file_name = 'anna_christie.txt'
file_name = 'act1.txt'

# Parsing Anna Christie
#
# Clear out the unnecessary material before Act I and
# after Act IV
#
# Make each "line" continuous: 
#   ACTOR + LINE_TEXT 
# followed by a single blank line
#
# Remove punctuation:
#   Periods
#   Exclamation marks
#   Question marks
#   Single and double quotes
# Extract words in square brackets -- these are Narratos' words

performer_name = oneOf( 'JOHNNY FIRST_LONGSHOREMAN \
                         SECOND_LONGSHOREMAN THE_POSTMAN \
                         LARRY CHRIS MARTHY ANNA THE_VOICE CHEIS \
                         BURKE JOHNSON NARRATOR' )('performer_name')
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

emdash_suppress = Suppress("--")
emdash_joined_words = script_word + emdash_suppress + script_word
# Or will parse the LONGEST match
actor_words = Or([four_hyphenated_words, three_hyphenated_words, emdash_joined_words, script_word])
actor_phrase = OneOrMore(actor_words)('actor_phrase')
open_bracket_suppress = Suppress("[")
close_bracket_suppress = Suppress("]")
narrator_phrase = open_bracket_suppress + OneOrMore(actor_words)('narrator_phrase') + close_bracket_suppress
script_phrase = Group(Or([narrator_phrase, actor_phrase]))
all_phrases = OneOrMore(script_phrase)('phrases')
script_line = performer_name + emdash_suppress + all_phrases

def get_script_line(file):
    script_line = ''
    while True:
        next_line = file.readline().lstrip("\xef\xbb\xbf").strip().translate(None, '().,?!;:')
        if next_line == '':
            break
        if script_line == '':
            script_line = next_line
        else:
            script_line = script_line + ' ' + next_line
    return script_line
    
def go():
    a = get_script_line(file)
    print a
    p = script_line.parseString(a)
    name = p['performer_name']
    print len(p['phrases'])
    for phrase in p['phrases']:
        try:
            np = phrase['narrator_phrase']
            print 'NARRATOR: %s' % (np,)
        except:
            print '%s: %s' % (name, phrase)
    return name
    
def check(file_name):
    '''
    Checks the parsing of a file simply by testing that
    all phrasese get parsed.  The test is simply that the
    last word in each source paragraph is the last word
    in the parsed text.
    '''
    file = open(file_name, 'r')
    while True:
        a = get_script_line(file)
        if a == '':
            print "Done"
            return
        print a
        p = script_line.parseString(a)
        split_a = a.strip("']").split()
        last_word = split_a[-1]
        p = script_line.parseString(a)
        phrases = p['phrases']
        last_phrase = phrases[-1]
        last_word_last_phrase = last_phrase[-1]
        if last_word == last_word_last_phrase:
            pass
        else:
            print a
            print last_word
            print last_word_last_phrase
            break
            
def go_until(performer):
    while True:
        if go() == performer:
            break
        else:
            pass
    return
                    
def count(file_name):
    file = open(file_name, 'r')
    performers = dict( JOHNNY=0, FIRST_LONGSHOREMAN=0, SECOND_LONGSHOREMAN=0, THE_POSTMAN=0, \
    LARRY=0, CHRIS=0, MARTHY=0, ANNA=0, THE_VOICE=0, CHEIS=0, BURKE=0, JOHNSON=0, NARRATOR=0)
    while True:
        a = get_script_line(file)
        if a=='':
            return performers
        p = script_line.parseString(a)
        name = p['performer_name']
        for phrase in p['phrases']:
            try:
                np = phrase['narrator_phrase']
                performers['NARRATOR'] += len(np)
            except:
                performers[name] += len(phrase)
    
file = open(file_name, 'r')
