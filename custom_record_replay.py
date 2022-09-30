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
import glob
from pathlib import Path


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


def clear_unused_recorded_voices() -> None:
    recorded_voices_folder = get_recorded_voices_folder()
    cid_list: list[int] = list[int]()
    invalid_cid_list: list[str] = list()
    for file in glob.glob(os.path.join(recorded_voices_folder, "*.wav")):
        if os.path.isfile(file):
            cid = Path(file).stem
            try:
                cid_list.append(int(cid))
            except ValueError:
                invalid_cid_list.append(cid)
    if cid_list:
        valid_cid_list: list[int] = []
        imax = len(cid_list) // 100
        if len(cid_list) % 100 == 0:
            imax -= 1
        for i in range(imax + 1):
            sql: str
            if i < imax or len(cid_list) % 100 != 1:
                cid_list_segment = cid_list[i*100:(i+1)*100] if i < imax else cid_list[i*100:]
                cid_set_text = str(cid_list_segment)[1:-1]
                # noinspection SqlNoDataSourceInspection
                sql = f"select id from cards where id in ({cid_set_text})"
            else:
                # noinspection SqlNoDataSourceInspection
                sql = f"select id from cards where id={cid_list[i * 100]}"
            valid_cid_list.extend(mw.col.db.list(sql))
        difference = set(cid_list).difference(set(valid_cid_list))
        for cid in difference:
            invalid_cid_list.append(str(cid))
    if invalid_cid_list:
        question = f"一共有{len(invalid_cid_list)}个不再使用的录音文件，请问是否清理？" \
            if is_chinese() else f"There are {len(invalid_cid_list)} unused " \
                                 f"recorded voices, would you like to clear them?"
        if askUser(question):
            for cid in invalid_cid_list:
                wav_path = Path(os.path.join(recorded_voices_folder, cid + '.wav'))
                wav_path.unlink(missing_ok=True)
            hint = f"清除了{len(invalid_cid_list)}个不再使用的录音文件。" if is_chinese() \
                else f"{len(invalid_cid_list)} unused recorded voices have been cleared."
            tooltip(hint)
    else:
        hint = "没有需要清理的录音文件。" if is_chinese() else "No unused recorded voices to be cleared."
        tooltip(hint)


def create_clear_unused_recorded_voice_menu_item() -> None:
    # create a new menu item, "test"
    title = "清理不再使用的录音文件" if is_chinese() else "Clear Unused Recorded Voices"
    action = QAction(title, mw)
    # set it to call testFunction when it's clicked
    qconnect(action.triggered, clear_unused_recorded_voices)
    # and add it to the tools menu
    mw.form.menuTools.addAction(action)


create_clear_unused_recorded_voice_menu_item()


def delete_all_recorded_voices() -> None:
    question = "删除后将无法恢复，请问是否要删除全部录音文件？" if is_chinese() \
        else "You can no longer recover the deleted recorded voices, are you sure to go on?"
    if askUser(question, defaultno=True):
        recorded_voices_folder = get_recorded_voices_folder()
        recorded_voices = glob.glob(os.path.join(recorded_voices_folder, "*.wav"))
        deleted_count = 0
        for file in recorded_voices:
            if os.path.isfile(file):
                try:
                    os.unlink(file)
                    deleted_count += 1
                except OSError:
                    pass
        hint = f"删除了{deleted_count}个录音文件" if is_chinese() \
            else f"{deleted_count} recorded voices have been deleted."
        tooltip(hint)


def create_delete_all_recorded_voices_menu_item() -> None:
    # create a new menu item, "test"
    title = "删除全部录音文件" if is_chinese() else "Remove All Recorded Voices"
    action = QAction(title, mw)
    # set it to call testFunction when it's clicked
    qconnect(action.triggered, delete_all_recorded_voices)
    # and add it to the tools menu
    mw.form.menuTools.addAction(action)


create_delete_all_recorded_voices_menu_item()
