import json
import pathlib
import pandas

from src.Kanjidic2Parser import Kanjidic2Parser
from src.KradfileParser import KradfileParser


def process_ka_data_csv(result_df):
    kadata_df = pandas.read_csv("data/kanji-data-media/ka_data.csv")
    kadata_keep_columns = [
        "kanji", "kname",
        # "kstroke", "kmeaning", "kgrade",
        # "kunyomi_ja",
        # "kunyomi",
        # "onyomi_ja",
        # "onyomi",
        "examples",
        # "radical", "rad_order", "rad_stroke", "rad_name_ja", "rad_name", "rad_meaning",
        # "rad_position_ja", "rad_position"
    ]
    kadata_remaps = {
        "kname": "ka_name",
        "kstroke": "ka_num_strokes",
        "kmeaning": "ka_english",
        "kgrade": "ka_grade",
        "kunyomi_ja": "ka_kunyomi_kana",
        "kunyomi": "ka_kunyomi_latin",
        "onyomi_ja": "ka_onyomi_kana",
        "onyomi": "ka_onyomi_latin",
        "examples": "ka_examples"
    }
    # Copy/rename columns from ka_data.csv to result_df
    for column in kadata_keep_columns:
        if column in kadata_remaps:
            result_df[kadata_remaps[column]] = kadata_df[column].values
        else:
            result_df[column] = kadata_df[column].values


def process_kanjidic2_xml(result_df):
    # Add kanjidic2 data to result_df
    kanjidic2 = Kanjidic2Parser(pathlib.Path("data/kanjidic2.xml"))
    kanjidic2.parse()
    for i, row in result_df.iterrows():
        kanji = row["kanji"]
        if kanji not in kanjidic2.kanji_dict:
            print(f"{kanji} not found in kanjidic2!")
        else:
            kanjidic2entry = kanjidic2.kanji_dict[kanji]
            result_df.loc[result_df["kanji"] == kanji, "onyomi"] = str.join(", ", kanjidic2entry.onyomi).rstrip(", ")
            result_df.loc[result_df["kanji"] == kanji, "kunyomi"] = str.join(", ", kanjidic2entry.kunyomi).rstrip(", ")
            result_df.loc[result_df["kanji"] == kanji, "nanori"] = str.join(", ", kanjidic2entry.nanori).rstrip(", ")
            result_df.loc[result_df["kanji"] == kanji, "english"] = str.join(", ", kanjidic2entry.english).rstrip(", ")
            result_df.loc[result_df["kanji"] == kanji, "jlpt"] = kanjidic2entry.jlpt
            result_df.loc[result_df["kanji"] == kanji, "strokes"] = kanjidic2entry.strokes
            result_df.loc[result_df["kanji"] == kanji, "usage_freq_2500"] = kanjidic2entry.freq
            result_df.loc[result_df["kanji"] == kanji, "grade"] = kanjidic2entry.grade


def process_kradfiles(result_df):
    # Add radicals from kradfile, kradfile2 to result_df
    krad = KradfileParser(pathlib.Path("data/kradfile"), pathlib.Path("data/kradfile2"))
    krad.parse()
    for i, row in result_df.iterrows():
        kanji = row["kanji"]
        if kanji not in krad.kanji_dict:
            print(f"{kanji} not found in kradfiles!")
        else:
            result_df.loc[result_df["kanji"] == kanji, "radicals"] = str.join(", ", krad.kanji_dict[kanji]).rstrip(", ")


def check_audio_files(result_df):
    for i, row in result_df.iterrows():
        kanji = row["kanji"]
        ka_name = row["ka_name"]
        examples = row["ka_examples"]
        examples_json = json.loads(examples)
        audio_paths = list(pathlib.Path("data/kanji-data-media/audio-ogg/").glob(f"{ka_name}_06_*.ogg"))
        if len(examples_json) != len(audio_paths):
            print(f"Audio files missing for examples of kanji '{kanji}' (files: {len(audio_paths)}, examples: {len(examples_json)})")
            for i in range(0, max(len(examples_json), len(audio_paths))):
                example = None
                audio_path = None
                try:
                    example = examples_json[i]
                except Exception:
                    pass
                try:
                    audio_path = audio_paths[i]
                except Exception:
                    pass
                if example is None or audio_path is None:
                    print(f"\t{example} -> {audio_path}")


def check_video_files(result_df):
    for i, row in result_df.iterrows():
        kanji = row["kanji"]
        ka_name = row["ka_name"]
        video_path = pathlib.Path(f"data/kanji-data-media/kanji-animations/{ka_name}_00.mp4")
        if not video_path.exists():
            print(f"Video for kanji '{kanji}' missing! Expected '{video_path}'")


if __name__ == '__main__':
    result_df = pandas.DataFrame()
    process_ka_data_csv(result_df)
    process_kanjidic2_xml(result_df)
    process_kradfiles(result_df)
    check_audio_files(result_df)
    check_video_files(result_df)
    result_df.to_csv("out/kanji_data.csv", index=False)
