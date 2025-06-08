from eth_account import Account
from loguru import logger
import primp
import random
import asyncio

from src.model.offchain.cex.instance import CexWithdraw
from src.model.projects.crustyswap.instance import CrustySwap
from src.model.projects.camp_loyalty.instance import CampLoyalty
from src.model.camp_network import CampNetwork
from src.model.help.stats import WalletStats
from src.model.onchain.web3_custom import Web3Custom
from src.utils.client import create_client
from src.utils.config import Config
from src.model.database.db_manager import Database
from src.utils.telegram_logger import send_telegram_message
from src.utils.decorators import retry_async
from src.utils.reader import read_private_keys


class Start:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        config: Config,
        discord_token: str,
        twitter_token: str,
        email: str,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.config = config
        self.discord_token = discord_token
        self.twitter_token = twitter_token
        self.email = email

        self.session: primp.AsyncClient | None = None
        self.camp_web3: Web3Custom | None = None
        self.camp_instance: CampNetwork | None = None
        self.loyalty: CampLoyalty | None = None

        self.wallet = Account.from_key(self.private_key)
        self.wallet_address = self.wallet.address

    @retry_async(default_value=False)
    async def initialize(self):
        try:
            self.session = await create_client(
                self.proxy, self.config.OTHERS.SKIP_SSL_VERIFICATION
            )
            self.camp_web3 = await Web3Custom.create(
                self.account_index,
                self.config.RPCS.CAMP_NETWORK,
                self.config.OTHERS.USE_PROXY_FOR_RPC,
                self.proxy,
                self.config.OTHERS.SKIP_SSL_VERIFICATION,
            )

            self.camp_instance = CampNetwork(
                self.account_index,
                self.session,
                self.camp_web3,
                self.config,
                self.wallet,
                self.discord_token,
                self.twitter_token,
                self.proxy,
                self.private_key,
                self.email,
            )

            return True
        except Exception as e:
            logger.error(f"{self.account_index} | Error: {e}")
            raise

    async def flow(self):
        try:
            db = Database()
            try:
                tasks = await db.get_wallet_pending_tasks(self.private_key)
            except Exception as e:
                if "no such table: wallets" in str(e):
                    logger.error(
                        f"🔴 [{self.account_index}] Database error: Database not created or wallets table not found. Please check the tutorial on how to create a database."
                    )
                    if self.config.SETTINGS.SEND_TELEGRAM_LOGS:
                        error_message = (
                            f"⚠️ Database Error Alert\n\n"
                            f"👤 Account #{self.account_index}\n"
                            f"💳 Wallet: <code>{self.private_key[:6]}...{self.private_key[-4:]}</code>\n"
                            f"❌ Error: Database not created or wallets table not found"
                        )
                        await send_telegram_message(self.config, error_message)
                    return False
                else:
                    logger.error(
                        f"🔴 [{self.account_index}] Failed to fetch tasks from database: {e}"
                    )
                    raise

            if not tasks:
                logger.warning(
                    f"⚠️ [{self.account_index}] No pending tasks found in database for this wallet. Exiting..."
                )
                if self.camp_web3:
                    await self.camp_web3.cleanup()
                return True

            pause = random.randint(
                self.config.SETTINGS.RANDOM_INITIALIZATION_PAUSE[0],
                self.config.SETTINGS.RANDOM_INITIALIZATION_PAUSE[1],
            )
            logger.info(
                f"⏳ [{self.account_index}] Initial pause: {pause} seconds before starting..."
            )
            await asyncio.sleep(pause)

            task_plan_msg = [f"{i+1}. {task['name']}" for i, task in enumerate(tasks)]
            logger.info(
                f"📋 [{self.account_index}] Task execution plan: {' | '.join(task_plan_msg)}"
            )

            completed_tasks = []
            failed_tasks = []

            # login to camp loyalty
            for task in tasks:
                if task["name"].lower().startswith("camp_loyalty"):
                    self.loyalty = CampLoyalty(self.camp_instance)
                    if not await self.loyalty.login():
                        logger.error(
                            f"🔴 [{self.account_index}] Failed to login to CampLoyalty"
                        )
                        self.loyalty = None
                    break

            # Execute tasks
            for task in tasks:
                task_name = task["name"]
                if task_name == "skip":
                    logger.info(f"⏭️ [{self.account_index}] Skipping task: {task_name}")
                    await db.update_task_status(
                        self.private_key, task_name, "completed"
                    )
                    completed_tasks.append(task_name)
                    await self.sleep(task_name)
                    continue

                logger.info(f"🚀 [{self.account_index}] Executing task: {task_name}")

                success = await self.execute_task(task_name)

                if success:
                    await db.update_task_status(
                        self.private_key, task_name, "completed"
                    )
                    completed_tasks.append(task_name)
                    await self.sleep(task_name)
                else:
                    failed_tasks.append(task_name)
                    if not self.config.FLOW.SKIP_FAILED_TASKS:
                        logger.error(
                            f"🔴 [{self.account_index}] Task {task_name} failed. Stopping wallet execution."
                        )
                        break
                    else:
                        logger.warning(
                            f"⚠️ [{self.account_index}] Task {task_name} failed. Continuing to next task."
                        )
                        await self.sleep(task_name)

            try:
                wallet_stats = WalletStats(self.config, self.camp_web3)
                await wallet_stats.get_wallet_stats(
                    self.private_key, self.account_index
                )
            except Exception as e:
                pass

            # Send Telegram message at the end
            if self.config.SETTINGS.SEND_TELEGRAM_LOGS:
                message = (
                    f"🤖 MedokLabs CampNetwork Bot Report\n\n"
                    f"👤 Account: #{self.account_index}\n"
                    f"💳 Wallet: <code>{self.private_key[:6]}...{self.private_key[-4:]}</code>\n\n"
                )

                if completed_tasks:
                    message += f"✅ Completed Tasks:\n"
                    for i, task in enumerate(completed_tasks, 1):
                        message += f"{i}. {task}\n"
                    message += "\n"

                if failed_tasks:
                    message += f"❌ Failed Tasks:\n"
                    for i, task in enumerate(failed_tasks, 1):
                        message += f"{i}. {task}\n"
                    message += "\n"

                total_tasks = len(tasks)
                completed_count = len(completed_tasks)
                message += (
                    f"📊 Statistics:\n"
                    f"📝 Total Tasks: {total_tasks}\n"
                    f"✅ Completed: {completed_count}\n"
                    f"❌ Failed: {len(failed_tasks)}\n"
                    f"📈 Success Rate: {(completed_count/total_tasks)*100:.1f}%\n\n"
                    f"⚙️ Settings:\n"
                    f"⏭️ Skip Failed: {'Yes' if self.config.FLOW.SKIP_FAILED_TASKS else 'No'}\n"
                )

                await send_telegram_message(self.config, message)

            return len(failed_tasks) == 0

        except Exception as e:
            logger.error(f"🔴 [{self.account_index}] Critical error: {e}")

            if self.config.SETTINGS.SEND_TELEGRAM_LOGS:
                error_message = (
                    f"⚠️ Critical Error Alert\n\n"
                    f"👤 Account #{self.account_index}\n"
                    f"💳 Wallet: <code>{self.private_key[:6]}...{self.private_key[-4:]}</code>\n"
                    f"❌ Error: {str(e)}"
                )
                await send_telegram_message(self.config, error_message)

            return False
        finally:
            # Cleanup resources
            try:
                if self.camp_web3:
                    await self.camp_web3.cleanup()
                logger.info(
                    f"✨ [{self.account_index}] All sessions closed successfully"
                )
            except Exception as e:
                logger.error(f"🔴 [{self.account_index}] Cleanup error: {e}")

            pause = random.randint(
                self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[0],
                self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[1],
            )
            logger.info(
                f"⏳ [{self.account_index}] Final pause: {pause} seconds before next account..."
            )
            await asyncio.sleep(pause)

    async def execute_task(self, task):
        """Execute a single task"""
        task = task.lower()

        if task == "faucet":
            return await self.camp_instance.request_faucet()

        if task == "crusty_refuel":
            crusty_swap = CrustySwap(
                self.account_index,
                self.session,
                self.camp_web3,
                self.config,
                self.wallet,
                self.proxy,
                self.private_key,
            )
            return await crusty_swap.refuel()
    
        if task == "crusty_refuel_from_one_to_all":
            private_keys = read_private_keys("data/private_keys.txt")

            crusty_swap = CrustySwap(
                1,
                self.session,
                self.camp_web3,
                self.config,
                Account.from_key(private_keys[0]),
                self.proxy,
                private_keys[0],
            )
            private_keys = private_keys[1:]
            return await crusty_swap.refuel_from_one_to_all(private_keys)
        
        if task == "cex_withdrawal":
            cex_withdrawal = CexWithdraw(
                self.account_index,
                self.private_key,
                self.config,
            )
            return await cex_withdrawal.withdraw()

        if task.startswith("camp_loyalty"):
            if not self.loyalty:
                logger.error(
                    f"🔴 [{self.account_index}] CampLoyalty login failed. Skipping task..."
                )
                return False

            if task == "camp_loyalty_connect_socials":
                return await self.loyalty.connect_socials()

            if task == "camp_loyalty_set_display_name":
                return await self.loyalty.set_display_name()

            # if task == "camp_loyalty_set_email":
            #     return await self.loyalty.set_email()

            if task.startswith("camp_loyalty_"):
                return await self.loyalty.complete_quests(task)
            
        logger.error(f"🔴 [{self.account_index}] Unknown task type: {task}")
        return False

    async def sleep(self, task_name: str):
        """Makes a random pause between actions"""
        pause = random.randint(
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
        )
        logger.info(
            f"⏳ [{self.account_index}] Pausing {pause} seconds after {task_name}"
        )
        await asyncio.sleep(pause)
