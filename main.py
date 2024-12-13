import time
import traceback
from tass.models import UserModel
from tass.tass import Tass
from utils.file_loader import load_web_app_data
from utils import logger
import random


class TassBeeh:
    def swipe_task(self, tass: Tass, profile: UserModel) -> None:
        try:
            min_swipe = 20
            max_swipe = 30
            energy_left = profile.energy

            if energy_left < max_swipe:
                logger.warning("Not enough energy to perform swipes. Skipping...")
                logger.info(f"Minimum Energy Required: {max_swipe}")
                logger.info(f"Energy left: {profile.energy}")
                return

            while energy_left > max_swipe:
                swipes = random.randint(min_swipe, max_swipe)
                logger.info(f"Registering {swipes} taps...")
                is_registered = tass.register_taps(swipes, swipes)
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

                self.quests_task(tass)
                time.sleep(5)
                start = time.time()
                self.swipe_task(tass, profile)
                end = time.time()
                logger.info(f"Swipe task completed in {(end - start) // 60} seconds.")
                logger.success("--- Swipe task completed. Waiting for next cycle ---")
                delay = random.randint(30 * 60, 60 * 60)
                logger.info(f"Waiting for {delay // 60} minutes...")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.error("Traceback: " + traceback.format_exc())
                logger.info("--- Main loop error. Waiting for 5 minutes ---")
                time.sleep(60 * 5)


if __name__ == "__main__":
    TassBeeh().run()
