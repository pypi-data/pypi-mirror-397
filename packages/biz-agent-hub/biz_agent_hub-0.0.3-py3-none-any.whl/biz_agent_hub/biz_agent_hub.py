from biz_agent_hub.supportbot_elite import SupportbotElite
from biz_agent_hub.scrap_agent import ScrapAgent
from biz_agent_hub.analytics_agent import AnalyticsAgent
from biz_agent_hub.browser_testing_agent import BrowserTestingAgent


class BizAgentHub:
    user_id: str
    api_key: str
    supportbot_elite: SupportbotElite
    def __init__(self, user_id: str, api_key: str) -> None:
        self.user_id = user_id
        self.api_key = api_key
        self.supportbot_elite = SupportbotElite(user_id, api_key)
        self.scrap_agent = ScrapAgent(user_id, api_key)
        self.analytics_agent = AnalyticsAgent(user_id, api_key)
        self.browser_testing_agent = BrowserTestingAgent(user_id, api_key)

