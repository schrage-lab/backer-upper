from pathlib import Path
from typing import Union
from datetime import date, datetime
import calendar
from dateutil.relativedelta import relativedelta


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
        # will return list of files with their attributes re: creation/modification time
        for path in src.iterdir():
            info = path.stat()
            created_on = datetime.fromtimestamp(info.st_ctime).date()
            if created_on < threshold:
                # rm file
                pass

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
        # if not beginning of week, don't prune
        if self.SfgBasic:
            if self._Today.weekday() != self.WeekBegins.getfirstweekday():
                return
        delta = date.today() - relativedelta(months=self.MonthlyBackupCount)
        threshold = self._Today - delta
        self._pruner(src=self.MonthlyBackupDirectoryLocal, threshold=threshold)


if __name__ == '__main__':
    root = Path.home().joinpath("Documents", "vms", "backups")

    sfg = SonFatherGrandfather(
        daily_local=root.joinpath("daily"),
        weekly_local=root.joinpath("weekly"),
        monthly_local=root.joinpath("monthly")
    )
    sfg.pruneDaily()
    sfg.pruneWeekly()
    sfg.pruneMonthly()
