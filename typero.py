import sys
import os
import time
import json
import random
# import msvcrt
from datetime import datetime
from file_parser import gather_lines


print('... running typero (%d)\n' % len(sys.argv))

if len(sys.argv) == 5 and sys.argv[1] == 'query':
    query_name = sys.argv[2]
    dir_path = sys.argv[3]
    regex_list = sys.argv[4].split('|')
    gather_lines(query_name, dir_path, regex_list)
    exit(1)

with open('config.json', 'r') as file:
    config = json.load(file)

os.system(config['clearCommand'])

with open(config['charFile'], 'r') as file:
    char_source = json.load(file)

chars = []
for kvp in char_source:
    for i in range(kvp[1]):
        chars.append(kvp[0])

prompt_word = ''
for i in range(config['charsPerLine']):
    prompt_word += chars[random.randrange(0, len(chars))]

print('\n\n---------------------------------------------')
print('%s\n' % prompt_word)

entered_chars = []
char_timers = []

while len(entered_chars) < len(prompt_word):
    start = time.perf_counter()
    char = msvcrt.getch()
    print(char.decode('ascii'), end='')
    sys.stdout.flush()
    elapsed = time.perf_counter() - start
    entered_chars.append(char.decode('ascii'))
    char_timers.append(elapsed)

print('\n\n--------------------------------------------')
errors = []
for i in range(len(prompt_word)):
    if entered_chars[i] != prompt_word[i]:
        errors.append(prompt_word[i])

now = datetime.now()
total_elapsed = round(sum(char_timers) * 1000, 1)
print('ELAPSED:\t\t%sms' % total_elapsed)
print('TIME per CHAR:\t\t%sms' % round(total_elapsed / config['charsPerLine'], 1))
print('ERRORS:\t\t\t%s' % ' '.join(errors))

# Calculate totals
with open(config['sessionFile'], 'r') as file:
    sessions = json.load(file)
    year_matches = [s for s in sessions if datetime.strptime(s['date'], config['dateFormat']).year == now.year]
    month_matches = [s for s in year_matches
                     if datetime.strptime(s['date'], config['dateFormat']).month == now.month]
    print('\nSESSIONS THIS MONTH:\t%d' % (len(month_matches) + 1))
    print('SESSIONS THIS YEAR:\t%d' % (len(year_matches) + 1))
    speeds = [round(s['elapsedMs'] / s['chars'], 0) for s in sessions]
    average = round(sum(speeds) / len(speeds), 0)
    herrors = {}
    for sess in sessions:
        for err in sess['errors']:
            if err in herrors:
                herrors[err] += 1
            else:
                herrors[err] = 1
    herrors = [[herr, herrors[herr]] for herr in herrors]
    herrors.sort(key=lambda val: val[1], reverse=True)

    print('FASTEST SPEED:\t\t%sms' % int(min(speeds)))
    print('SLOWEST SPEED:\t\t%sms' % int(max(speeds)))
    print('AVERAGE SPEED:\t\t%sms' % int(average))
    worst_str = 'WORST CHARACTERS:\n\t'
    for i in range(config['worstCharsDisplayed']):
        worst_str += '%s\t%d\n\t' % (herrors[i][0], herrors[i][1])
    print(worst_str)

with open(config['sessionFile'], 'r') as file:
    sessions = json.load(file)
    sessions.append({
        "id": sessions[-1]['id'] + 1,
        "date": now.strftime(config['dateFormat']),
        "errors": ''.join(errors),
        "chars": len(prompt_word),
        "elapsedMs": total_elapsed
    })
with open(config['sessionFile'], 'w') as file:
    json.dump(sessions, file)

print('\n... exiting')

