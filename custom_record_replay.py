import os.path
import shutil
from typing import Optional
# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect, showText, askUser, tooltip
# import all the Qt GUI library
from aqt.qt import *

import anki
import anki.lang
from aqt import gui_hooks
from aqt.main import AnkiQt


def _ensure_exists(path: str) -> str:
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_recorded_voices_folder() -> str:
    profile_folder: str = mw.pm.profileFolder()
    recorded_voices_folder = _ensure_exists(os.path.join(profile_folder, 'recorded_voices'))
    return recorded_voices_folder


def on_reviewer_will_replay_recording(path: str) -> str:
    recorded_voices_folder = get_recorded_voices_folder()
    card = mw.reviewer.card
    card_id = card.id
    card_wav_path = os.path.join(recorded_voices_folder, f'{card_id}.wav')
    if path and os.path.basename(path) == 'rec.wav':
        if os.path.exists(path):
            # User has recorded a new voice, move it to [profile folder]/recorded_voices
            shutil.move(path, card_wav_path)
            mw.reviewer._recordedAudio = card_wav_path
            path = card_wav_path
        elif os.path.exists(card_wav_path):
            # User has not recorded a voice since he starts to study the current card this time,
            # but there is a voice previously recorded for the card, replay it
            mw.reviewer._recordedAudio = card_wav_path
            path = card_wav_path
        else:
            # User has not recorded any voice for the current card, and there is no voice
            # previously recorded for the card, so do nothing here
            pass
    else:
        if os.path.exists(card_wav_path):
            # User has not recorded a voice since he starts to study the current card this time,
            # but there is a voice previously recorded for the card, replay it
            path = card_wav_path
        else:
            # User has not recorded a voice since he starts to study the current card this time,
            # and there is no voice previously recorded for the card, so we need to return an
            # empty path to tell user he has not recorded his own voice
            path = ""
    return path


gui_hooks.reviewer_will_replay_recording.append(on_reviewer_will_replay_recording)


def is_chinese() -> bool:
    return anki.lang.current_lang == 'zh-CN'


def check_recorded_voice() -> None:
    recorded_voices_folder = get_recorded_voices_folder()
    import glob
    from pathlib import Path
    cid_set: set[int] = set[int]()
    invalid_cid_set: set[str] = set()
    for file in glob.glob(os.path.join(recorded_voices_folder, "*.wav")):
        if os.path.isfile(file):
            cid = Path(file).stem
            try:
                cid_set.add(int(cid))
            except ValueError:
                invalid_cid_set.add(cid)
    if cid_set:
        sql: str
        if len(cid_set) > 1:
            cid_set_text = str(cid_set)[1:-1]
            # noinspection SqlNoDataSourceInspection
            sql = f"select id from cards where id in ({cid_set_text})"
        else:
            # noinspection SqlNoDataSourceInspection
            sql = f"select id from cards where id={list(cid_set)[0]}"
        valid_cid_set = set(mw.col.db.list(sql))
        for cid in cid_set.difference(valid_cid_set):
            invalid_cid_set.add(str(cid))
    if invalid_cid_set:
        question = f"一共有{len(invalid_cid_set)}个不再使用的录音文件，请问是否清理？" \
            if is_chinese() else f"There are {len(invalid_cid_set)} unused " \
                                 f"recorded voices, would you like to clear them?"
        if askUser(question):
            for cid in invalid_cid_set:
                wav_path = Path(os.path.join(recorded_voices_folder, cid + '.wav'))
                wav_path.unlink(missing_ok=True)
            hint = f"清除了{len(invalid_cid_set)}个不再使用的录音文件。" if is_chinese() \
                else f"{len(invalid_cid_set)} unused recorded voices have been cleared."
            tooltip(hint)
    else:
        hint = "没有需要清理的录音文件。" if is_chinese() else "No unused recorded voices to be cleared."
        tooltip(hint)


def create_check_unused_recorded_voice_menu_item():
    # create a new menu item, "test"
    title = "清理录音文件" if is_chinese() else "check recorded voices"
    action = QAction(title, mw)
    # set it to call testFunction when it's clicked
    qconnect(action.triggered, check_recorded_voice)
    # and add it to the tools menu
    mw.form.menuTools.addAction(action)


create_check_unused_recorded_voice_menu_item()
