import asyncio
import random
from loguru import logger
from eth_account import Account
from src.model.help.captcha import NoCaptcha, Solvium
from src.model.onchain.web3_custom import Web3Custom
import primp

from src.utils.decorators import retry_async
from src.utils.config import Config
from src.model.camp_network.constants import CampNetworkProtocol
from src.utils.constants import EXPLORER_URL_CAMP_NETWORK


class FaucetService:
    def __init__(self, camp_network_instance: CampNetworkProtocol):
        self.camp_network = camp_network_instance

    @retry_async(default_value=False)
    async def request_faucet(self):
        try:
            logger.info(f"{self.camp_network.account_index} | Starting faucet...")

            logger.info(
                f"{self.camp_network.account_index} | Solving hCaptcha challenge with Solvium..."
            )
            solvium = Solvium(
                api_key=self.camp_network.config.CAPTCHA.SOLVIUM_API_KEY,
                session=self.camp_network.session,
                proxy=self.camp_network.proxy,
            )

            captcha_token = await solvium.solve_captcha(
                sitekey="5b86452e-488a-4f62-bd32-a332445e2f51",
                pageurl="https://faucet.campnetwork.xyz/",
            )

            if captcha_token is None:
                raise Exception("Captcha not solved")

            logger.success(f"{self.camp_network.account_index} | Captcha solved for faucet")

            headers = {
                'accept': '*/*',
                'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7,zh-TW;q=0.6,zh;q=0.5,uk;q=0.4',
                'content-type': 'application/json',
                'h-captcha-response': captcha_token,
                'origin': 'https://faucet.campnetwork.xyz',
                'priority': 'u=1, i',
                'referer': 'https://faucet.campnetwork.xyz/',
                'sec-ch-ua': '"Chromium";v="133", "Google Chrome";v="133", "Not.A/Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            }

            json_data = {
                'address': self.camp_network.wallet.address,
            }

            response = await self.camp_network.session.post('https://faucet-go-production.up.railway.app/api/claim', headers=headers, json=json_data)

            if (
                "context deadline exceeded" in response.text or 
                "nonce too low" in response.text or 
                "replacement transaction underpriced" in response.text
            ):
                raise Exception(f"Faucet is not available for the moment")

            if "Bot detected" in response.text:
                logger.error(f"{self.camp_network.account_index} | Your wallet is not available for the faucet. Wallet must have some transactions")
                return False
            
            if "Your IP has exceeded the rate limit" in response.text:
                logger.error(f"{self.camp_network.account_index} | {response.json()['msg']}")
                return False
            
            if response.status_code != 200:
                raise Exception(
                    f"failed to request faucet: {response.status_code} | {response.text}"
                )

            logger.success(
                f"{self.camp_network.account_index} | Successfully requested faucet"
            )
            return True
            
        except Exception as e:
            if 'Too many successful transactions for this wallet address, please try again later' in str(e):
                logger.success(
                    f"{self.camp_network.account_index} | Wait 24 hours before next request"
                )
                return True
                
            if 'Wallet does not meet eligibility requirements. Required: either 0.05 ETH balance OR 3+ transactions on Ethereum mainnet.' in str(e):
                logger.error(
                    f"{self.camp_network.account_index} | Wallet does not meet eligibility requirements. Required: either 0.05 ETH balance OR 3+ transactions on Ethereum mainnet."
                )
                return False

            random_pause = random.randint(
                self.camp_network.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                self.camp_network.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.error(
                f"{self.camp_network.account_index} | Faucet error: {e}. Sleeping {random_pause} seconds..."
            )
            await asyncio.sleep(random_pause)
            raise 
