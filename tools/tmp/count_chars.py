from pathlib import Path
import re
import datetime

p = Path('E:/DONT_TOUCH/10M-2025-Testing/book/1208.2025.newbook.md')
s = p.read_text(encoding='utf-8')
chars = len(s)
chars_no_ws = len(re.sub(r"\s+","", s))
# Note: 'word_tokens_ascii' is rough; Chinese is counted in chars above
words_like = len(re.findall(r"\w+", s))
ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
print(f"file: {p}")
print(f"total_chars: {chars}")
print(f"chars_excluding_whitespace: {chars_no_ws}")
print(f"word_tokens_ascii: {words_like}")
report = Path('E:/DONT_TOUCH/10M-2025-Testing/tools/reports/book_1208_charcount_'+ts+'.txt')
report.write_text(f"file: {p}\ntotal_chars: {chars}\nchars_excluding_whitespace: {chars_no_ws}\nword_tokens_ascii: {words_like}\n", encoding='utf-8')
print(f"report: {report}")
