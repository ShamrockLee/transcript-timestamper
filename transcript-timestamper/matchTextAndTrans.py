# -*- coding: utf-8 -*-
# %%
import pandas as pd
import opencc
import jellyfish
import re
from pandarallel import pandarallel

# pip install ipywidgets

pandarallel.initialize(progress_bar=True)
# %%
FILEPATH_WHISPER_TEXT = "./data/text_wav/output_video.csv"
FILEPATH_PDF_TEXT = "./data/text_pdf_script/2024071209_1.xlsx"

whisper_text = pd.read_csv(FILEPATH_WHISPER_TEXT)
pdf_text = pd.read_excel(FILEPATH_PDF_TEXT)
pdf_text.reset_index(drop=False, inplace=True)
pdf_text.rename(columns={"index": "id"}, inplace=True)


# %%
# convert whisper_text to traditional chinese
def convert_to_traditional_chinese(converter_s2t, text):
    try:
        return converter_s2t.convert(text)
    except:
        return ""


converter = opencc.OpenCC("s2t.json")
whisper_text["text"] = whisper_text["text"].apply(
    lambda x: convert_to_traditional_chinese(converter, x)
)
# remove empty text
whisper_text = whisper_text[whisper_text["text"] != ""]


# %%
# pdf split text to multiple row by ["…", "？", "「", "」", "「"
def split_text_ary(text):
    # Regular expression to match non-Chinese characters
    pattern = re.compile(r"[^\u4e00-\u9fff]")
    # Find all non-Chinese characters
    non_chinese_chars = pattern.findall(text)
    split_text = set(non_chinese_chars)
    # Find all non-English and number characters
    pattern = re.compile(r"[^a-zA-Z0-9]")
    split_text = pattern.findall("".join(split_text))
    return split_text


delimiters = split_text_ary("".join(pdf_text.content.values))
delimiters = ["…", "？", "─", "、", "，", "！", "。"]
pattern = "|".join(map(re.escape, delimiters))
pdf_text["split_text"] = pdf_text["content"].apply(lambda x: re.split(pattern, x))
pdf_text_explode = pdf_text.explode("split_text")
pdf_text_explode = pdf_text_explode.dropna(subset=["split_text"])
pdf_text_explode["content_seq"] = pdf_text_explode.groupby("id").cumcount()
# combine the id and content_seq to get the unique id
pdf_text_explode["id"] = pdf_text_explode["id"].astype(str)
pdf_text_explode["content_seq"] = pdf_text_explode["content_seq"].astype(str)
pdf_text_explode["id"] = pdf_text_explode["id"] + "@" + pdf_text_explode["content_seq"]
pdf_text_explode.reset_index(drop=True, inplace=True)


# %%
def combine_row_same_text(input_pd):
    start_ind = 0
    end_ind = 0
    for ind in range(1, len(input_pd.index)):
        ind_now = input_pd.index[ind]
        ind_pre = input_pd.index[ind - 1]
        if input_pd.loc[ind_now, "text"] == input_pd.loc[ind_pre, "text"]:
            # print(ind_now)
            if start_ind == 0 and end_ind == 0:
                start_ind = ind_pre
                end_ind = ind_now
            else:
                end_ind = ind_now

            # last row
            if ind_now == input_pd.index[ind] and start_ind != 0 and end_ind != 0:
                input_pd.loc[start_ind:end_ind, "start"] = input_pd.loc[
                    start_ind, "start"
                ]
                input_pd.loc[start_ind:end_ind, "end"] = input_pd.loc[end_ind, "end"]
        else:
            if start_ind == 0 and end_ind == 0:
                continue
            else:
                input_pd.loc[start_ind:end_ind, "start"] = input_pd.loc[
                    start_ind, "start"
                ]
                input_pd.loc[start_ind:end_ind, "end"] = input_pd.loc[end_ind, "end"]
                start_ind = 0
                end_ind = 0
    return input_pd.drop_duplicates()


whisper_text_combine = combine_row_same_text(whisper_text).copy()
whisper_text_combine["id"] = list(range(len(whisper_text_combine.index)))
whisper_text_combine["id"] = whisper_text_combine["id"].astype(str)


whisper_text_combine = whisper_text_combine.iloc[0:100,]


# %%
def caculate_similarity(row_whisper):
    sim_list = []
    for ind_pdf in range(len(pdf_text_explode.index)):
        index_pdf = pdf_text_explode.index[ind_pdf]
        row_pdf = pdf_text_explode.loc[index_pdf, :]
        similarity = jellyfish.jaro_similarity(
            row_whisper["text"], row_pdf["split_text"]
        )
        sim_list.append(
            {
                "id_whisper": row_whisper["id"],
                "id_pdf": row_pdf["id"],
                "similarity": similarity,
            }
        )
    sim_pd = pd.DataFrame(sim_list)
    # select the value larger than 0
    sim_pd = sim_pd[sim_pd["similarity"] > 0]
    if sim_pd.empty:
        return sim_pd
    # select the value of max similarity
    select_sim_max = sim_pd[sim_pd["similarity"] == sim_pd["similarity"].max()]
    return select_sim_max


jaro_similarity_pd_parallelapply_list = whisper_text_combine.parallel_apply(
    caculate_similarity, axis=1
)
jaro_similarity_pd_parallelapply_list = [
    df for df in jaro_similarity_pd_parallelapply_list
]
jaro_similarity_pd_parallelapply = pd.concat(jaro_similarity_pd_parallelapply_list)
# %%
jaro_similarity_pd_res = jaro_similarity_pd_parallelapply.merge(
    whisper_text_combine, left_on="id_whisper", right_on="id"
).merge(pdf_text_explode, left_on="id_pdf", right_on="id")
# %%
jaro_similarity_pd_res.to_excel("./jaro_similarity_pd_res.xlsx", index=False)
# %%
# iter whisper_text_combine to caculate the similarity


jaro_similarity_pd_apply_list = whisper_text_combine.apply(caculate_similarity, axis=1)
jaro_similarity_pd_apply_list = [df for df in jaro_similarity_pd_apply_list]
jaro_similarity_pd_apply = pd.concat(jaro_similarity_pd_apply_list)
# %%

# %%


# %%
test_pd = whisper_text_combine.iloc[-10:, :]
# %%
# when the text is same the end of the time is the same
# when the text is different the end of the time is different
# test_pd = whisper_text.iloc[0:140, :].copy()
start_ind = 0
end_ind = 0
for ind in range(1, len(test_pd.index)):
    ind_now = test_pd.index[ind]
    ind_pre = test_pd.index[ind - 1]
    if test_pd.loc[ind_now, "text"] == test_pd.loc[ind_pre, "text"]:
        print(ind_now)
        if start_ind == 0 and end_ind == 0:
            start_ind = ind_pre
            end_ind = ind_now
        else:
            end_ind = ind_now

        # last row
        if ind_now == test_pd.index[ind] and start_ind != 0 and end_ind != 0:
            test_pd.loc[start_ind:end_ind, "start"] = test_pd.loc[start_ind, "start"]
            test_pd.loc[start_ind:end_ind, "end"] = test_pd.loc[end_ind, "end"]
    else:
        if start_ind == 0 and end_ind == 0:
            continue
        else:
            test_pd.loc[start_ind:end_ind, "start"] = test_pd.loc[start_ind, "start"]
            test_pd.loc[start_ind:end_ind, "end"] = test_pd.loc[end_ind, "end"]
            start_ind = 0
            end_ind = 0

# drop all same rows
test_drop = test_pd.drop_duplicates()
# %%
whisper_text.text.values[0:400]
# %%
pdf_text.content.values[0:10]
# %%
import re

text = "".join(pdf_text.content.values)

# Regular expression to match non-Chinese characters
pattern = re.compile(r"[^\u4e00-\u9fff]")
# Find all non-Chinese characters
non_chinese_chars = pattern.findall(text)
unique_non_chinese_chars = set(non_chinese_chars)
# Find all non-English and number characters
pattern = re.compile(r"[^a-zA-Z0-9]")
unique_non_eng_chars = pattern.findall("".join(unique_non_chinese_chars))
print(unique_non_eng_chars)

# %%
# Sample string
text = "apple,banana;cherry|date"

# List of delimiters
delimiters = [",", ";", "|"]

# Create a regular expression pattern from the list of delimiters
pattern = "|".join(map(re.escape, delimiters))

# Split the string using the pattern
result = re.split(pattern, text)
print(result)

# %%
df = pd.DataFrame({"a": [1, 1, 1, 2, 2, 3, 2], "b": [1, 1, 2, 1, 1, 2, 2]})
df["idx"] = df.groupby("a").cumcount() + 1
# %%
# Add a sequence column within each group
df["idx"] = df.groupby("a").cumcount() + 1
# %%
