import datetime
from typing import Optional
import json

import torch
import sounddevice as sd
from UnlimitedGPT import ChatGPT

from common.log import logger
from common.tts_model import ModelHolder
from infer import InvalidToneError
from text.japanese import kata_tone2phone_tone, text_normalize, g2kata_tone

model_dir = "model_assets"
device = "cuda" if torch.cuda.is_available() else "cpu"
model_holder = ModelHolder(model_dir, device)

MODEL_NAME = "MODEL_NAME_HERE"
SESSION_TOKEN = "YOUR_TOKEN_HERE"

def tts_fn(
    model_name,
    model_path,
    text,
    language,
    reference_audio_path,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    line_split,
    split_interval,
    assist_text,
    assist_text_weight,
    use_assist_text,
    style,
    style_weight,
    kata_tone_json_str,
    use_tone,
    speaker,
):
    model_holder.load_model_gr(model_name, model_path)

    wrong_tone_message = ""
    kata_tone: Optional[list[tuple[str, int]]] = None
    if use_tone and kata_tone_json_str != "":
        if language != "JP":
            logger.warning("Only Japanese is supported for tone generation.")
            wrong_tone_message = "アクセント指定は現在日本語のみ対応しています。"
        if line_split:
            logger.warning("Tone generation is not supported for line split.")
            wrong_tone_message = (
                "アクセント指定は改行で分けて生成を使わない場合のみ対応しています。"
            )
        try:
            kata_tone = []
            json_data = json.loads(kata_tone_json_str)
            # tupleを使うように変換
            for kana, tone in json_data:
                assert isinstance(kana, str) and tone in (0, 1), f"{kana}, {tone}"
                kata_tone.append((kana, tone))
        except Exception as e:
            logger.warning(f"Error occurred when parsing kana_tone_json: {e}")
            wrong_tone_message = f"アクセント指定が不正です: {e}"
            kata_tone = None

    # toneは実際に音声合成に代入される際のみnot Noneになる
    tone: Optional[list[int]] = None
    if kata_tone is not None:
        phone_tone = kata_tone2phone_tone(kata_tone)
        tone = [t for _, t in phone_tone]

    speaker_id = model_holder.current_model.spk2id[speaker]

    start_time = datetime.datetime.now()

    try:
        sr, audio = model_holder.current_model.infer(
            text=text,
            language=language,
            reference_audio_path=reference_audio_path,
            sdp_ratio=sdp_ratio,
            noise=noise_scale,
            noisew=noise_scale_w,
            length=length_scale,
            line_split=line_split,
            split_interval=split_interval,
            assist_text=assist_text,
            assist_text_weight=assist_text_weight,
            use_assist_text=use_assist_text,
            style=style,
            style_weight=style_weight,
            given_tone=tone,
            sid=speaker_id,
        )
    except InvalidToneError as e:
        logger.error(f"Tone error: {e}")
        return f"Error: アクセント指定が不正です:\n{e}", None, kata_tone_json_str
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return f"Error: {e}", None, kata_tone_json_str

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    if tone is None and language == "JP":
        # アクセント指定に使えるようにアクセント情報を返す
        norm_text = text_normalize(text)
        kata_tone = g2kata_tone(norm_text)
        kata_tone_json_str = json.dumps(kata_tone, ensure_ascii=False)
    elif tone is None:
        kata_tone_json_str = ""
    message = f"Success, time: {duration} seconds."
    if wrong_tone_message != "":
        message = wrong_tone_message + "\n" + message
    return message, (sr, audio), kata_tone_json_str

def get_tts_output(text):
    _, audio_output, _ = tts_fn(
        model_name=MODEL_NAME,
        model_path=f"model_assets\{MODEL_NAME}\{MODEL_NAME}_e100_s24300.safetensors",
        text=text,
        language="JP",
        reference_audio_path=None,
        sdp_ratio=0.2,
        noise_scale=0.6,
        noise_scale_w=0.8,
        length_scale=1,
        line_split=True,
        split_interval=0.5,
        assist_text="",
        assist_text_weight=1,
        use_assist_text=False,
        style="Neutral",
        style_weight=5,
        kata_tone_json_str="",
        use_tone=False,
        speaker={MODEL_NAME}
    )
    return audio_output

if __name__ == "__main__":
    called = input("呼ばれ方を入力してください:")
    calling = input("呼び方を入力してください:")
    api = ChatGPT(SESSION_TOKEN)

    with open("prompt.txt", "r", encoding="utf-8") as file:
        prompt = file.read()

    res = api.send_message(prompt.format(called=called, calling=calling)).response

    audio_output = get_tts_output(res)
    sd.play(audio_output[1], audio_output[0])
    sd.wait()

    try:    
        while True:
            s = input("返信:")
            if s == "!help":
                print("!exit:終了")
            elif s == "!exit":
                break
            res = api.send_message(s).response
            audio_output = get_tts_output(res)
            sd.play(audio_output[1], audio_output[0])
            sd.wait()
        api.logout()
    except KeyboardInterrupt:
        api.logout()
        exit()