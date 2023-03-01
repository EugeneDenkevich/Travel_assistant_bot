import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery


# setting callback_data prefix and parts
calendar_callback = CallbackData('simple_calendar', 'act', 'year', 'month', 'day')


class SimpleCalendar:


    async def month_rus(self, n: int) -> str:
        month = {1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь", 7: "Июль",
                8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}
        
        for i in month.keys():
            if i == n:
                return month[i]
        return "Something was wrong"

    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month,
        date: str = None
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """
        
        inline_kb = InlineKeyboardMarkup(row_width=7)
        ignore_callback = calendar_callback.new("IGNORE", year, month, 0)  # for buttons with no answer
        # First row - Month
        inline_kb.row()

        if date != None:
            inline_kb.insert(InlineKeyboardButton(
                            "◀",
                            callback_data=calendar_callback.new("PREV-MONTH", year, int(date.split('/')[1]), 1)
                            )
            )
            inline_kb.insert(InlineKeyboardButton(
                            f"{await self.month_rus(int(date.split('/')[1]))}",
                            callback_data=ignore_callback
                            )
            )
            inline_kb.insert(InlineKeyboardButton(
                            "▶",
                            callback_data=calendar_callback.new("NEXT-MONTH", year, int(date.split('/')[1]), 1)
                            )
            )

        else:
            inline_kb.insert(InlineKeyboardButton(
                "◀",
                callback_data=calendar_callback.new("PREV-MONTH", year, month, 1)
            ))
            inline_kb.insert(InlineKeyboardButton(
                f'{await self.month_rus(month)}',
                callback_data=ignore_callback
            ))
            inline_kb.insert(InlineKeyboardButton(
                "▶",
                callback_data=calendar_callback.new("NEXT-MONTH", year, month, 1)
            ))
        # Second row - Week Days
        inline_kb.row()
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if(day == 0):
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("DAY", year, month, day)
                ))

        # Last row - Buttons
        inline_kb.row()
        if date != None:
            inline_kb.insert(InlineKeyboardButton(
            "◀", callback_data=calendar_callback.new("PREV-YEAR", int(date.split('/')[2]), month, day)
            ))
            inline_kb.insert(InlineKeyboardButton(f"{str(date.split('/')[2])}", callback_data=ignore_callback))
            inline_kb.insert(InlineKeyboardButton(
            "▶", callback_data=calendar_callback.new("NEXT-YEAR", int(date.split('/')[2]), month, day)
            ))
        else:

            inline_kb.insert(InlineKeyboardButton(
            "◀", callback_data=calendar_callback.new("PREV-YEAR", year, month, day)
            ))
            inline_kb.insert(InlineKeyboardButton(f"{str(year)}", callback_data=ignore_callback))
            inline_kb.insert(InlineKeyboardButton(
            "▶", callback_data=calendar_callback.new("NEXT-YEAR", year, month, day)
            ))

        return inline_kb

    async def process_selection(self, query: CallbackQuery, data: CallbackData) -> tuple:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a tuple (Boolean,datetime), indicating if a date is selected
                    and returning the date if so.
        """
        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)
        # processing empty buttons, answering with no action
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        # user picked a day button, return date
        if data['act'] == "DAY":
            return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
        # user navigates to previous year, editing message with new calendar
        if data['act'] == "PREV-YEAR":
            prev_date = temp_date - timedelta(days=366)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next year, editing message with new calendar
        if data['act'] == "NEXT-YEAR":
            next_date = temp_date + timedelta(days=366)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # user navigates to previous month, editing message with new calendar
        if data['act'] == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next month, editing message with new calendar
        if data['act'] == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # at some point user clicks DAY button, returning date
        return return_data
