from typing import Dict, Optional, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class CheckInModel(BaseModel):
    checkInsStreak: int = Field(..., description="Current streak of check-ins")
    lastCheckInDate: datetime = Field(..., description="Date of the last check-in")
    checkInExperience: int = Field(..., description="Experience earned from check-ins")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class PrayerStatusModel(BaseModel):
    name: str = Field(..., description="Name of the prayer")
    status: str = Field(
        ..., description="Status of the prayer (claimed or not-claimed)"
    )
    date: datetime = Field(..., description="Date and time of the prayer")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class PrayerDataModel(BaseModel):
    nextPrayer: datetime = Field(..., description="Next prayer date and time")
    streak: int = Field(..., description="Current streak of prayers")
    prayerStatuses: Dict[str, PrayerStatusModel] = Field(
        ..., description="Prayer statuses for each prayer"
    )

    @classmethod
    def from_dict(cls, data: dict):
        prayer_statuses = {
            key: PrayerStatusModel.from_dict(value)
            for key, value in data["prayerStatuses"].items()
        }
        return cls(
            nextPrayer=datetime.fromisoformat(data["nextPrayer"]),
            streak=data["streak"],
            prayerStatuses=prayer_statuses,
        )


class Progress(BaseModel):
    current: int
    total: int


class Quest(BaseModel):
    id: int
    name: str
    questType: str
    actionLink: Optional[HttpUrl] = None
    actionLinks: Optional[dict[str, HttpUrl]] = None
    isHidden: bool
    finishCondition: str
    rewardExp: int
    isUserAchieved: bool
    isActive: bool
    progress: Optional[Progress] = None
    isNew: Optional[bool] = None


class QuestData(BaseModel):
    regularQuests: List[Quest]
    dailyQuests: List[Quest]
    partnerQuests: List[Quest]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class ReferralsModel(BaseModel):
    firstTier: Dict[str, int] = Field(..., description="Data for first-tier referrals")
    secondTier: Dict[str, int] = Field(
        ..., description="Data for second-tier referrals"
    )


class TapsModel(BaseModel):
    firstLevel: int = Field(..., description="Taps at the first level")
    secondLevel: int = Field(..., description="Taps at the second level")


class UserModel(BaseModel):
    telegramId: int = Field(..., description="Telegram ID of the user")
    experience: int = Field(..., description="User's total experience points")
    referrals: ReferralsModel = Field(..., description="Referral data for the user")
    totalTaps: int = Field(..., description="Total taps by the user")
    taps: TapsModel = Field(..., description="Details of taps at each level")
    tapsToday: int = Field(..., description="Number of taps by the user today")
    achievementsCount: int = Field(..., description="Count of achievements unlocked")
    haqqAddress: Optional[str] = Field(None, description="Haqq address if available")
    energy: int = Field(..., description="Current energy level of the user")
    energyBoosterFinishDate: Optional[datetime] = Field(
        None, description="Finish date for energy booster"
    )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class AdBooster(BaseModel):
    cooldownDate: datetime = Field(..., description="Date and time of the cooldown")
    status: str = Field(
        ..., description="Status of the ad booster (active or inactive)"
    )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
