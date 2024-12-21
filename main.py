import time
import traceback
from tass.models import UserModel
from tass.tass import Tass
from utils.file_loader import load_web_app_data
from utils import logger
import random

from datetime import datetime, timedelta, timezone


class TassBeeh:
    def __init__(self) -> None:
        self.last_auth_time: datetime = datetime.now(timezone.utc) - timedelta(days=1)
        self.auth_refresh_delay: int = 30

    def refresh_auth(self, tass: Tass) -> None:
        gap = (datetime.now(timezone.utc) - self.last_auth_time).total_seconds()
        if gap >= self.auth_refresh_delay:
            logger.info(
                f"Last authentication token refresh time: {self.last_auth_time}"
            )
            logger.info("Refreshing authentication token...")
            tass.refresh_auth_token()
            self.last_auth_time = datetime.now(timezone.utc)

    def booster_swipe(
        self, user: UserModel, tass: Tass, min_swipe: int, max_swipe: int
    ) -> None:
        logger.info("Energy Booster period has started.")

        if user.energyBoosterFinishDate is None:
            return
        finish_date = user.energyBoosterFinishDate
        total_energy_gained = 0

        time.sleep(11)

        while datetime.now(timezone.utc) + timedelta(seconds=10) < finish_date:
            self.refresh_auth(tass)
            swipes = random.randint(min_swipe, max_swipe)
            is_registered = tass.register_taps(swipes)
            if not is_registered:
                logger.error("Failed to register taps.")
                logger.info("--- Waiting for 10 seconds ---")
                time.sleep(10)
                continue
            total_energy_gained += swipes
            logger.info("--- Waiting for 2-5 seconds ---")
            time.sleep(random.randint(2, 5))

        logger.success(f"Total Energy Gained: {total_energy_gained}")
        logger.info("Energy Booster period has ended.")

    def swipe_task(self, tass: Tass, profile: UserModel) -> None:
        try:
            min_swipe = 20
            max_swipe = 30
            self.ad_boost(tass)
            self.booster_swipe(profile, tass, min_swipe, max_swipe)
            energy_left = profile.energy

            if energy_left < max_swipe:
                logger.warning("Not enough energy to perform swipes. Skipping...")
                logger.info(f"Minimum Energy Required: {max_swipe}")
                logger.info(f"Energy left: {profile.energy}")
                return

            while energy_left > max_swipe:
                self.refresh_auth(tass)
                swipes = random.randint(min_swipe, max_swipe)
                is_registered = tass.register_taps(swipes)
                if not is_registered:
                    logger.error("Failed to register taps.")
                    logger.info("--- Waiting for 10 seconds ---")
                    time.sleep(10)
                    continue
                energy_left -= swipes
                logger.success(
                    f"Swiped {swipes} times. Remaining energy: {energy_left}"
                )
                logger.info("--- Waiting for 5-10 seconds ---")
                time.sleep(random.randint(5, 10))

            logger.warning("Energy completely exhausted.")
        except Exception as e:
            logger.error(f"Error during swipe task: {e}")
            logger.error("Traceback: " + traceback.format_exc())

    def quests_task(self, tass: Tass):
        logger.info("Task: Quests")
        quests = tass.get_quests()
        if not quests:
            logger.warning("Failed to retrieve quest information.")
            raise Exception("Failed to retrieve quest information.")

        tass.claim_quests(quests.regularQuests, "Regular")
        tass.claim_quests(quests.dailyQuests, "Daily")
        tass.claim_quests(quests.partnerQuests, "Partner")

        logger.success("Quests completed.")

    def ad_boost(self, tass: Tass) -> bool:
        logger.info("Task: Ad Booster")
        profile = tass.get_profile_info()

        if not profile:
            logger.warning("Failed to retrieve profile information.")
            raise Exception("Failed to retrieve profile information.")
        adboost = tass.ad_booster(profile)
        if not adboost:
            logger.warning("Failed to retrieve ad booster information.")
            return False
        if adboost.status == "active":
            logger.info("Ad Booster is active.")
            return True
        logger.info("Ad Booster is inactive.")
        return False

    def run(self):
        while True:
            try:
                web_app_data = load_web_app_data()
                tass = Tass(web_app_data)
                profile = tass.get_profile_info()
                if not profile:
                    logger.warning("Failed to retrieve profile information.")
                    raise Exception("Failed to retrieve profile information.")

                tass.log_profile(profile)
                time.sleep(5)

                tass.check_in()
                time.sleep(5)
                logger.info(f"Energy {profile.energy}")
                if profile.energy < 3000:
                    tass.refill_energy()
                    time.sleep(5)

                time.sleep(5)
                start = time.time()
                self.swipe_task(tass, profile)
                end = time.time()
                logger.info(f"Swipe task completed in {(end - start) // 60} seconds.")
                logger.success("--- Swipe task completed. Waiting for next cycle ---")
                self.quests_task(tass)
                delay = random.randint(5 * 60, 10 * 60)
                logger.info(f"Waiting for {delay // 60} minutes...")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.error("Traceback: " + traceback.format_exc())
                logger.info("--- Main loop error. Waiting for 5 minutes ---")
                time.sleep(60 * 5)


if __name__ == "__main__":
    TassBeeh().run()
