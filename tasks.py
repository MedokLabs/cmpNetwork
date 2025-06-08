TASKS = ["CRUSTY_SWAP"]

### LOYALTY WORKS ONLY WITH STATIS PROXIES!!! YOU CAN USE RESIDENTIAL BUT WITHOUT IP ROTATION ###
### LOYALTY WORKS ONLY WITH STATIS PROXIES!!! YOU CAN USE RESIDENTIAL BUT WITHOUT IP ROTATION ###
### LOYALTY WORKS ONLY WITH STATIS PROXIES!!! YOU CAN USE RESIDENTIAL BUT WITHOUT IP ROTATION ### 

CRUSTY_SWAP = [
    # "cex_withdrawal",
    "crusty_refuel",
    # "crusty_refuel_from_one_to_all",
]

CAMP_LOYALTY = [
    "camp_loyalty_connect_socials",
    "camp_loyalty_set_display_name",
    "camp_loyalty_complete_quests",
]

# FOR EXAMPLE ONLY, USE YOUR OWN TASKS PRESET
FULL_TASK = [
    "faucet",
    "camp_loyalty_connect_socials",
    "camp_loyalty_set_display_name",
    "camp_loyalty_complete_quests",
]

SKIP = ["skip"]

FAUCET = ["faucet"]

CAMP_LOYALTY_CONNECT_SOCIALS = ["camp_loyalty_connect_socials"]
CAMP_LOYALTY_SET_DISPLAY_NAME = ["camp_loyalty_set_display_name"]
CAMP_LOYALTY_COMPLETE_QUESTS = ["camp_loyalty_complete_quests"]

# CAMPAIGNS
CAMP_LOYALTY_STORYCHAIN = ["camp_loyalty_storychain"]
CAMP_LOYALTY_TOKEN_TAILS = ["camp_loyalty_token_tails"]
CAMP_LOYALTY_AWANA = ["camp_loyalty_awana"]
CAMP_LOYALTY_PICTOGRAPHS = ["camp_loyalty_pictographs"]
CAMP_LOYALTY_HITMAKR = ["camp_loyalty_hitmakr"]
CAMP_LOYALTY_PANENKA = ["camp_loyalty_panenka"]
CAMP_LOYALTY_SCOREPLAY = ["camp_loyalty_scoreplay"]
CAMP_LOYALTY_WIDE_WORLDS = ["camp_loyalty_wide_worlds"]
CAMP_LOYALTY_ENTERTAINM = ["camp_loyalty_entertainm"]
CAMP_LOYALTY_REWARDED_TV = ["camp_loyalty_rewarded_tv"]
CAMP_LOYALTY_SPORTING_CRISTAL = ["camp_loyalty_sporting_cristal"]
CAMP_LOYALTY_BELGRANO = ["camp_loyalty_belgrano"]
CAMP_LOYALTY_ARCOIN = ["camp_loyalty_arcoin"]
CAMP_LOYALTY_KRAFT = ["camp_loyalty_kraft"]
CAMP_LOYALTY_SUMMITX = ["camp_loyalty_summitx"]
CAMP_LOYALTY_PIXUDI = ["camp_loyalty_pixudi"]
CAMP_LOYALTY_CLUSTERS = ["camp_loyalty_clusters"]
CAMP_LOYALTY_JUKEBLOX = ["camp_loyalty_jukeblox"]
CAMP_LOYALTY_CAMP_NETWORK = ["camp_loyalty_camp_network"]
"""
EN:
You can create your own task with the modules you need 
and add it to the TASKS list or use our ready-made preset tasks.

( ) - Means that all of the modules inside the brackets will be executed 
in random order
[ ] - Means that only one of the modules inside the brackets will be executed 
on random
SEE THE EXAMPLE BELOW:

RU:
Вы можете создать свою задачу с модулями, которые вам нужны, 
и добавить ее в список TASKS, см. пример ниже:

( ) - означает, что все модули внутри скобок будут выполнены в случайном порядке
[ ] - означает, что будет выполнен только один из модулей внутри скобок в случайном порядке
СМОТРИТЕ ПРИМЕР НИЖЕ:

CHINESE:
你可以创建自己的任务，使用你需要的模块，
并将其添加到TASKS列表中，请参见下面的示例：

( ) - 表示括号内的所有模块将按随机顺序执行
[ ] - 表示括号内的模块将按随机顺序执行

--------------------------------
!!! IMPORTANT !!!
EXAMPLE | ПРИМЕР | 示例:

TASKS = [
    "CREATE_YOUR_OWN_TASK",
]
CREATE_YOUR_OWN_TASK = [
    "faucet",
    ("camp_loyalty_entertainm", "camp_loyalty_connect_socials"),
    ["camp_loyalty_awana", "camp_loyalty_camp_network"],
    "camp_loyalty_jukeblox",
]
--------------------------------


BELOW ARE THE READY-MADE TASKS THAT YOU CAN USE:
СНИЗУ ПРИВЕДЕНЫ ГОТОВЫЕ ПРИМЕРЫ ЗАДАЧ, КОТОРЫЕ ВЫ МОЖЕТЕ ИСПОЛЬЗОВАТЬ:
以下是您可以使用的现成任务：


--- ALL TASKS ---

faucet - Request Faucet on Camp Network - https://faucet.campnetwork.xyz/

*** LOYALTY ***
camp_loyalty_connect_socials - Connect socials on Loyalty - https://loyalty.campnetwork.xyz/loyalty?editProfile=1&modalTab=social
camp_loyalty_set_display_name - Set display name on Loyalty - https://loyalty.campnetwork.xyz/loyalty?editProfile=1&modalTab=displayName
camp_loyalty_complete_quests - Complete quests on Loyalty - https://loyalty.campnetwork.xyz/loyalty?editProfile=1&modalTab=quests

*** LOYALTY CAMPAIGNS ***
camp_loyalty_storychain - StoryChain
camp_loyalty_token_tails - Token Tails
camp_loyalty_awana - AWANA
camp_loyalty_pictographs - Pictographs
camp_loyalty_hitmakr - Hitmakr
camp_loyalty_panenka - Panenka
camp_loyalty_scoreplay - Scoreplay
camp_loyalty_wide_worlds - Wide Worlds
camp_loyalty_entertainm - EntertainM
camp_loyalty_rewarded_tv - RewardedTV
camp_loyalty_sporting_cristal - Sporting Cristal
camp_loyalty_belgrano - Belgrano
camp_loyalty_arcoin - ARCOIN
camp_loyalty_kraft - Kraft
camp_loyalty_summitx - SummitX
camp_loyalty_pixudi - Pixudi
camp_loyalty_clusters - Clusters
camp_loyalty_jukeblox - JukeBlox
camp_loyalty_camp_network - Camp Network

crusty_refuel - refuel CAMP at https://www.crustyswap.com/
crusty_refuel_from_one_to_all - refuel CAMP from one to all wallets at https://www.crustyswap.com/
cex_withdrawal - withdraw ETH from cex exchange (okx, bitget)

OTHERS
skip - Skip task (use it for random OR if you want to see logs)
"""
