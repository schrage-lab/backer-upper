import argparse
from pathlib import Path
from typing import Union
import datetime
import calendar


class SonFatherGrandfather:
    """
    Remove snapshots based on age
    Week begins on Monday 12am (0000 hours)
    Make backups and store appropriately
        1) Keep all snapshots from Mon-Sun in the "daily" backup directory
        2) Keep the Sunday snapshot --> move to the "weekly" backup directory
        3) If day == first day of month --> move to "monthly" backup directory
    Prune the backups
        4) At beginning of week --> remove snapshots from previous Mon-Sat in the "daily" backup directory
        5) If day == first day of month --> remove snapshots from "weekly" backup directory
        6) If day == first day of month --> remove snapshots form "monthly" backup directory if >3 months old
    """
    # todo: add logic/attributes to customize the age of backups e.g. only keep recent monthly backup, keep 18 daily
    #  backups, etc.
    def __init__(
            self,
            *,
            sfg_basic: bool = True,
            week_begins: str = "monday",
            month_begins: int = 1,
            daily_count: int = 7,
            weekly_count: int = 4,
            monthly_count: int = 3,
            daily_local: Union[str, Path],
            weekly_local: Union[str, Path],
            monthly_local: Union[str, Path],
            daily_remote: Union[str, Path, None] = None,
            weekly_remote: Union[str, Path] = None,
            monthly_remote: Union[str, Path] = None
    ) -> None:
        """
        Initialize class
        :param sfg_basic: Use the basic SFG rotation. This entails keeping:
                            - the past 7 days of daily files + days up to the beginning of the week (up to 13 files). At
                                the beginning of the week, the oldest 7 files will be deleted;
                            - the past 4 weeks of weekly files. This will be the same as the daily backup for the
                                beginning of the week.
                            - the past 3 months of monthly files. This will be the same as the daily backup for the
                                beginning of the month.
        :param week_begins: Day that the week begins. Options: "monday", "tuesday", "wednesday", "thursday",
                            "friday", "saturday", "sunday" (default = "monday").
        :param month_begins: Day of month that will be taken to represent the beginning of the monthly period. Currently
                            has limited capabilities and only supports 1-28 due to differences in monthly durations.
                            Will be added in future versions.
        """

        # ensure day is valid
        days_of_week = self._getDaysOfWeek()
        if not str.lower(week_begins) in days_of_week:
            raise ValueError("Unknown day")

        self.WeekBegins = str.lower(week_begins)

        # set the day for the month beginning
        today = datetime.datetime.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]

        # account for months with fewer days
        if month_begins > days_in_month:
            month_begins = days_in_month
        self.MonthBegins = month_begins

        # set directories
        self.DailyBackupDirctoryLocal = daily_local
        self.WeeklyBackupDirectoryLocal = weekly_local
        self.MonthlyBackupDirectoryLocal = monthly_local
        self.DailyBackupDirectoryRemote = daily_remote
        self.WeeklyBackupDirectoryRemote = weekly_remote
        self.MonthlyBackupDirectoryRemote = monthly_remote

    @staticmethod
    def _getDaysOfWeek() -> tuple:
        """
        Get the string name of each day of the week.

        :return: names of days
        :rtype: tuple
        """

        days = list()
        for i in range(0, 7):
            weekday = datetime.date.today() + datetime.timedelta(days=i)
            days.append(weekday.strftime("%A").lower())
        return tuple(days)

    def pruneDaily(self):
        pass

    def pruneWeekly(self):
        pass

    def pruneMonthly(self):
        pass
