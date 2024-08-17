# -*- coding: utf-8 -*-
# %%
from pypdf import PdfReader
from itertools import chain
import pandas as pd
import re


def select_text(texts):
    texts = list(filter(None, texts))
    # select text isn't  "   協 123" "協   2  "
    pattern = re.compile(r"\s*協\s*\d+\s*")
    texts = [s for s in texts if not pattern.match(s)]
    texts = [s + "\n" for s in texts]
    for ind in range(1, len(texts)):
        if texts[ind][0].isspace():
            texts[ind - 1] = texts[ind - 1][:-1]
    texts = "".join(texts).split("\n")
    texts = [s.replace(" ", "") for s in texts]
    texts = list(filter(None, texts))
    return texts


# %%
FILENAME = "2024071209_1"
reader = PdfReader("./data/pdf/{}.pdf".format(FILENAME))

# %%
pdf_text = [
    reader.pages[ind].extract_text(extraction_mode="layout").split("\n")
    for ind in range(len(reader.pages))
]
pdf_text = list(chain(*pdf_text))
# %%
# texts = list(filter(None, pdf_text))
# # select text isn't  "   協 123" "協   2  "
# pattern = re.compile(r"\s*協\s*\d+\s*")
# texts = [s for s in texts if not pattern.match(s)]
# %%
preprocess_str = select_text(pdf_text)
# select text containg ":" and "："
preprocess_str = [s for s in preprocess_str if "：" in s or ":" in s]
preprocess_str = [s for s in preprocess_str if "附錄" not in s]
# str to dict with key: name, value: content
preprocess_dict = []
for s in preprocess_str:
    test_split = s.split("：", 1)
    if len(test_split) != 2:
        print(s)
    else:
        s_dict = {"name": test_split[0], "content": test_split[1]}
        preprocess_dict.append(s_dict)

# %%
pd.DataFrame(preprocess_dict).to_excel(
    "./data/text_pdf_script/{}.xlsx".format(FILENAME), index=False
)
# %%
