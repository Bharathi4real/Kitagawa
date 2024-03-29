from math import ceil
from typing import Dict, List
from telegram import InlineKeyboardButton, MAX_MESSAGE_LENGTH
from Marin import NO_LOAD


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i * 3 : (i + 1) * 3] for i in range((len(modules) + 3 - 1) // 3)]

    round_num = len(modules) / 3
    calc = len(modules) - round(round_num)
    if calc in [1, 2]:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / 10)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 10:
        pairs = pairs[modulo_page * 10 : 10 * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "⮜", callback_data="{}_prev({})".format(prefix, modulo_page)
                ),
                EqInlineKeyboardButton("Back", callback_data="yone_back"),
                EqInlineKeyboardButton(
                    "⮞", callback_data="{}_next({})".format(prefix, modulo_page)
                ),
            )
        ]

    else:
        pairs += [[EqInlineKeyboardButton("Back", callback_data="yone_back")]]

    return pairs


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def revert_buttons(buttons):
    return "".join(
        f"\n[{btn.name}](buttonurl://{btn.url}:same)"
        if btn.same_line
        else f"\n[{btn.name}](buttonurl://{btn.url})"
        for btn in buttons
    )


def build_keyboard_parser(bot, chat_id, buttons):
    keyb = []
    for btn in buttons:
        if btn.url == "{rules}":
            btn.url = "http://t.me/{}?start={}".format(bot.username, chat_id)
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def split_message(msg: str) -> List[str]:
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < MAX_MESSAGE_LENGTH:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    # Else statement at the end of the for loop, so append the leftover string.
    result.append(small_msg)

    return result


def is_module_loaded(name):
    return name not in NO_LOAD
