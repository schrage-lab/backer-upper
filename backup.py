from pathlib import Path
from typing import Union
from datetime import date, datetime
import calendar
from dateutil.relativedelta import relativedelta


class SonFatherGrandfather:
    def __init__(
            self,
            *,
            sfg_basic: bool = True,
            week_begins: str = "monday",
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
        """

        self.SfgBasic = sfg_basic
        if self.SfgBasic:
            self.DailyBackupCount = 7
            self.WeeklyBackupCount = 4
            self.MonthlyBackupCount = 3
        else:
            self.DailyBackupCount = daily_count
            self.WeeklyBackupCount = weekly_count
            self.MonthlyBackupCount = monthly_count
        self.WeekBegins = calendar.setfirstweekday(getattr(calendar, week_begins.upper()))

        # set directories
        self.DailyBackupDirctoryLocal = daily_local
        self.WeeklyBackupDirectoryLocal = weekly_local
        self.MonthlyBackupDirectoryLocal = monthly_local
        self.DailyBackupDirectoryRemote = daily_remote
        self.WeeklyBackupDirectoryRemote = weekly_remote
        self.MonthlyBackupDirectoryRemote = monthly_remote

        # protected attributes
        self._Today = date.today()
        self._MonthBegins = 1

    @property
    def MonthBegins(self):
        return self._MonthBegins

    @MonthBegins.setter
    def MonthBegins(self, value) -> None:
        if value != 1:
            raise AttributeError("Protected attribute.")

    @MonthBegins.deleter
    def MonthBegins(self) -> None:
        raise AttributeError("Protected attribute.")

    @property
    def Today(self):
        return self._Today

    @Today.setter
    def Today(self, value) -> None:
        if not isinstance(value, date) and value != date.today():
            raise AttributeError("Protected attribute.")

    @Today.deleter
    def Today(self) -> None:
        raise AttributeError("Protected attribute.")

    def _pruner(self, *, src: Path, threshold: datetime.date) -> None:
        for file in src.iterdir():
            info = file.stat()
            created_on = datetime.fromtimestamp(info.st_ctime).date()
            if created_on < threshold:
                file.unlink()

    # todo: make a wrapper??
    def pruneDaily(self) -> None:
        # if not beginning of week, don't prune
        if self.SfgBasic:
            if self._Today.weekday() != self.WeekBegins.getfirstweekday():
                return
        delta = relativedelta(days=self.DailyBackupCount)
        threshold = self._Today - delta
        self._pruner(src=self.DailyBackupDirctoryLocal, threshold=threshold)

    def pruneWeekly(self) -> None:
        # if not beginning of week, don't prune
        if self.SfgBasic:
            if self._Today.weekday() != self.WeekBegins.getfirstweekday():
                return
        delta = relativedelta(weeks=self.WeeklyBackupCount)
        threshold = self._Today - delta
        self._pruner(src=self.WeeklyBackupDirectoryLocal, threshold=threshold)

    def pruneMonthly(self) -> None:
        # if not beginning of month, don't prune
        if self.SfgBasic:
            if self._Today.day != self.MonthBegins:
                return
        delta = date.today() - relativedelta(months=self.MonthlyBackupCount)
        threshold = self._Today - delta
        self._pruner(src=self.MonthlyBackupDirectoryLocal, threshold=threshold)
