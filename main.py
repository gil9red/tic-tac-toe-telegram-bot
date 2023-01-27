#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import time
import os
import re

# pip install python-telegram-bot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    MessageHandler, CommandHandler, Filters, CallbackQueryHandler, Updater, CallbackContext, Defaults
)

import config
import logic

from common import get_logger, log_func, reply_error, fill_string_pattern


PATTERN_CELL = re.compile(r'^(?P<x>-?\d)x(?P<y>-?\d)=(?P<value>-?\d)$')


CHARS = {
    logic.COMP: '🤖',
    logic.HUMAN: '😬',
    logic.EMPTY: ' '
}


# TODO: All phrases into separate variables


log = get_logger(__file__)


def get_int_from_match(match: re.Match, name: str, default: int = None) -> int | None:
    try:
        return int(match[name])
    except:
        return default


@log_func(log)
def on_start(update: Update, _: CallbackContext):
    update.effective_message.reply_text(
        'Write something or click button!',
        reply_markup=ReplyKeyboardMarkup.from_button('Go!', resize_keyboard=True)
    )


@log_func(log)
def on_request(update: Update, context: CallbackContext):
    board = logic.get_empty_board()

    keyboard = [
        [
            InlineKeyboardButton(
                CHARS[cell],
                callback_data=fill_string_pattern(PATTERN_CELL, x, y, cell)
            )
            for y, cell in enumerate(row)
        ]
        for x, row in enumerate(board)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.effective_message.reply_text(
        'You turn...',
        reply_markup=reply_markup
    )


@log_func(log)
def on_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query

    reply_markup = query.message.reply_markup
    inline_keyboard = reply_markup.inline_keyboard

    board: list[list[int]] = []
    for row in inline_keyboard:
        board.append([])
        for button in row:
            m = PATTERN_CELL.search(button.callback_data)
            board[-1].append(
                get_int_from_match(m, 'value')
            )

    if logic.game_over(board) or not logic.empty_cells(board):
        query.answer('Game is over!')
        return

    query.answer()

    x = get_int_from_match(context.match, 'x')
    y = get_int_from_match(context.match, 'y')
    value = get_int_from_match(context.match, 'value')

    if value != logic.EMPTY:
        text = "It's already selected!"
        query.message.edit_text(text, reply_markup=reply_markup)
        return

    value = logic.HUMAN

    button = inline_keyboard[x][y]
    button.text = CHARS[value]
    button.callback_data = fill_string_pattern(PATTERN_CELL, x, y, value)

    board[x][y] = value
    if logic.wins(board, logic.HUMAN):
        text = 'You win! 👍'
        query.message.edit_text(text, reply_markup=reply_markup)
        return

    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    query.message.edit_reply_markup(reply_markup=reply_markup)

    query.message.edit_text('AI think...', reply_markup=reply_markup)
    time.sleep(1)

    x, y = logic.ai_choice(board)
    if x == -1 or y == -1:
        if logic.wins(board, logic.COMP):
            text = 'AI win! 👎'
        else:
            text = 'Draw! 👍'

        query.message.edit_text(text, reply_markup=reply_markup)
        return

    value = logic.COMP
    board[x][y] = value

    button = inline_keyboard[x][y]
    button.text = CHARS[value]
    button.callback_data = fill_string_pattern(PATTERN_CELL, x, y, value)

    if logic.wins(board, logic.COMP):
        text = 'AI win! 👎'
        query.message.edit_text(text, reply_markup=reply_markup)
        return

    query.message.edit_text('You turn...', reply_markup=reply_markup)


def main():
    log.debug('Start')

    cpu_count = os.cpu_count()
    workers = cpu_count
    log.debug(f'System: CPU_COUNT={cpu_count}, WORKERS={workers}')

    updater = Updater(
        config.TOKEN,
        workers=workers,
        defaults=Defaults(run_async=True),
    )
    bot = updater.bot
    log.debug(f'Bot name {bot.first_name!r} ({bot.name})')

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', on_start))
    dp.add_handler(MessageHandler(Filters.text, on_request))
    dp.add_handler(CallbackQueryHandler(on_callback_query, pattern=PATTERN_CELL))

    dp.add_error_handler(lambda update, context: reply_error(log, update, context))

    updater.start_polling()
    updater.idle()

    log.debug('Finish')


if __name__ == '__main__':
    timeout = 15

    while True:
        try:
            main()
        except:
            log.exception('')

            log.info(f'Restarting the bot after {timeout} seconds')
            time.sleep(timeout)
