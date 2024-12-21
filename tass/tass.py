import random
import time
import requests
from typing import Optional
from tass.coordinates import Coordinates
from tass.endpoints import Endpoints
from tass.headers import COMMON_HEADERS
from tass.models import (
    AdBooster,
    CheckInModel,
    PrayerDataModel,
    Quest,
    QuestData,
    UserModel,
)
from utils import logger
from datetime import datetime, timedelta, timezone


class Tass:
    def __init__(self, web_app_data: str):
        self.blocklist_quests = [
            "connect_haqq_wallet",
            "islm_join_telegram_channel",
            "islm_join_telegram_chat",
            "watch_ads_daily",
            "join_the_commuity",
            "follow_us_on_telegram",
        ]
        self.web_app_data = web_app_data
        self.session = requests.Session()
        self.auth_token = self.__get_auth_token(self.web_app_data)
        if not self.auth_token:
            logger.error("Error: Failed to retrieve Auth Token.")
            raise Exception("Could not retrieve Auth Token.")

    def __generate_swipes(self, swipes_count: int) -> list:
        swipes = []
        for _ in range(swipes_count):
            co = Coordinates.new()
            swipes.append(
                {
                    "start": {"x": co.start_x, "y": co.start_y},
                    "end": {"x": co.end_x, "y": co.end_y},
                    "dateTime": int(time.time() * 1000),
                }
            )
            time.sleep(0.2)
        return swipes

    def __get_auth_token(self, web_app_data: str) -> Optional[str]:
        payload = {"webAppData": web_app_data}
        response = self.session.post(
            Endpoints.AUTH_TOKEN_URL,
            json=payload,
            headers=COMMON_HEADERS,
        )
        response_data = response.json()
        token = response_data.get("token")
        if not token:
            logger.error("Error: Failed to retrieve Auth Token.")
            logger.error(response.text)
            logger.error(response.status_code)
            return
        return token

    def refresh_auth_token(self):
        self.auth_token = self.__get_auth_token(self.web_app_data)

    def register_taps(self, swipes_count: int) -> bool:
        swipes = self.__generate_swipes(swipes_count)
        payload = {"swipes": swipes, "taps": len(swipes)}
        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        response = self.session.post(
            Endpoints.REGISTER_TAPS_URL, json=payload, headers=headers
        )
        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return False
        if response.status_code != 200:
            logger.error(
                f"Error: Failed to register taps. Status Code: {response.status_code}"
            )
            logger.error(response.text)
            logger.error(response.status_code)
            return False
        logger.success(f"Taps {swipes_count} registered successfully.")
        return True

    def get_profile_info(self) -> Optional[UserModel]:
        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        response = self.session.get(Endpoints.PROFILE_URL, headers=headers)
        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return
        return UserModel.from_dict(response.json())

    def log_profile(self, profile: UserModel):
        logger.info(f"User ID: {profile.telegramId}")
        logger.info(f"Total Experience: {profile.experience}")
        logger.info(f"Referrals: {profile.referrals.firstTier}")
        logger.info(f"Second-Tier Referrals: {profile.referrals.secondTier}")
        logger.info(f"Total Taps: {profile.totalTaps}")
        logger.info(f"Taps First Level: {profile.taps.firstLevel}")
        logger.info(f"Taps Second Level: {profile.taps.secondLevel}")
        logger.info(f"Taps Today: {profile.tapsToday}")
        logger.info(f"Achievements Count: {profile.achievementsCount}")
        logger.info(f"Haqq Address: {profile.haqqAddress}")
        logger.info(f"Energy: {profile.energy}")
        logger.info(f"Energy Booster Finish Date: {profile.energyBoosterFinishDate}")

    def get_checkin_info(
        self,
    ) -> Optional[CheckInModel]:
        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        response = self.session.get(Endpoints.CHECK_IN_URL, headers=headers)
        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return
        return CheckInModel.from_dict(response.json())

    def check_in(self):
        logger.info("Trying to check in")
        check_in_info = self.get_checkin_info()
        if not check_in_info:
            logger.warning("Failed to retrieve check-in information.")
            return

        current_date = datetime.now(timezone.utc).date()
        last_check_in_date = check_in_info.lastCheckInDate.date()

        if last_check_in_date == current_date:
            logger.warning("Already checked in today.")
            return

        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }

        response = self.session.post(Endpoints.CHECK_IN_URL, headers=headers)

        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to check-in. Status Code: {response.status_code}"
            )
            logger.error(response.text)
            return

        logger.success("Check-in completed successfully.")

    def __get_ready_to_claim_key(self, data: PrayerDataModel) -> Optional[str]:
        return next(
            (
                key
                for key, status in data.prayerStatuses.items()
                if status.status == "ready-to-claim"
            ),
            None,
        )

    def refill_energy(self):
        prayer_data = self.get_prayer_data()
        if not prayer_data:
            logger.warning("Failed to retrieve prayer data.")
            return

        now = datetime.now(timezone.utc)

        ready_to_claim_key = self.__get_ready_to_claim_key(prayer_data)

        if not ready_to_claim_key:
            if now < prayer_data.nextPrayer:
                logger.warning(
                    f"Cannot refill energy. Prayer not yet started: {prayer_data.nextPrayer}"
                )
                return

        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        logger.info(f"{ready_to_claim_key} is ready to claim. Refilling energy...")
        response = self.session.post(Endpoints.REFILL_ENERGY_URL, headers=headers)

        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to refill energy. Status Code: {response.status_code}"
            )
            logger.error(response.text)
            return

        logger.success("Energy refilled successfully.")

    def get_prayer_data(self):
        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        response = self.session.get(Endpoints.PRAYER_STATUS_URL, headers=headers)

        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to get prayer status. Status Code: {response.status_code}"
            )
            logger.error(response.text)
            return

        return PrayerDataModel.from_dict(response.json())

    def get_quests(self):
        self.refresh_auth_token()
        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        response = self.session.get(Endpoints.QUESTS_URL, headers=headers)

        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to get quests. Status Code: {response.status_code}"
            )
            logger.error(response.text)
            return

        return QuestData.from_dict(response.json())

    def claim_quest(self, quest: Quest) -> bool:
        if quest.name in self.blocklist_quests:
            logger.warning(f"Quest '{quest.name}' is in block list.")
            return False

        if quest.isHidden:
            logger.warning(f"Quest '{quest.name}' is hidden.")
            return False

        if quest.isUserAchieved:
            logger.info(f"Quest '{quest.name}' has already been claimed.")
            return False

        logger.info(f"Claiming daily quest: {quest.name}")

        if quest.progress and quest.progress.current != quest.progress.total:
            logger.warning(f"Quest '{quest.name}' not completed yet.")
            return False

        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        response = self.session.post(
            Endpoints.VERIFY_QUEST_URL, json={"questId": quest.id}, headers=headers
        )

        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return False

        if response.status_code == 404:
            logger.error(f"Error: Quest not found: {quest.id}")
            return False

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to claim daily quest. Status Code: {response.status_code}"
            )
            logger.error(response.text)
            return False

        logger.success(f"Daily quest '{quest.name}' claimed successfully.")
        time.sleep(1)
        return response.json().get("isVerified") is True

    def claim_quests(self, quests: list[Quest], quest_type: str):
        logger.info(f"Performing {quest_type} Quests.")
        logger.info(f"Total Quests: {len(quests)}")
        for quest in quests:
            is_claimed = self.claim_quest(quest)
            if is_claimed:
                logger.info("Wait a few seconds before claiming another quest.")
                time.sleep(random.randint(1, 5))

    def ad_booster(self, user: UserModel) -> Optional[AdBooster]:
        if user.energyBoosterFinishDate is None:
            logger.info("User does not have an energy booster.")
            return
        if user.energyBoosterFinishDate + timedelta(minutes=10) > datetime.now(
            timezone.utc
        ):
            logger.info(
                "Advertise has already received an advertisement in the last 10 minutes."
            )
            return

        self.refresh_auth_token()
        headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {self.auth_token}",
        }
        response = self.session.post(Endpoints.AD_BOOSTER_URL, headers=headers)

        if response.status_code == 401:
            logger.warning("Authorization token expired")
            self.refresh_auth_token()
            return

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to advertise. Status Code: {response.status_code}"
            )
            logger.error(response.text)
            return

        return AdBooster.from_dict(response.json())
