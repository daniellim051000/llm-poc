from api_tools import (
    ActiveContractsTool,
    CustomerContractsTool,
    CustomerInvoicesTool,
    CustomerSearchTool,
    CustomerServicesTool,
    InvoiceSearchTool,
    ItemSearchTool,
    SerialLookupTool,
    ServiceHistoryTool,
    WebSearchTool,
)
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI


class BusinessDataAgent:
    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        deployment_name: str,
        api_version: str = "2024-02-15-preview",
    ):
        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version,
            deployment_name=deployment_name,
            temperature=0,
        )

        self.tools = [
            CustomerSearchTool(),
            CustomerInvoicesTool(),
            CustomerContractsTool(),
            CustomerServicesTool(),
            ItemSearchTool(),
            InvoiceSearchTool(),
            ActiveContractsTool(),
            SerialLookupTool(),
            ServiceHistoryTool(),
            WebSearchTool(),
        ]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a business data assistant that helps users query information about customers, invoices, contracts, items, services, and web information.

                        You have access to tools that can retrieve data from a business management system and search the web for additional information. Use these tools to answer user questions accurately.

                        When answering questions:
                        1. Use the appropriate tools to gather the necessary data
                        2. Provide clear, concise answers based on the retrieved data
                        3. If you need to look up a customer first to get their ID, do that before querying their related data
                        4. For questions about specific brands (like Ricoh), use the item search tool
                        5. For contract/SLA questions, use the active contracts tool
                        6. For service history, use the service history tool
                        7. For web searches, industry trends, news, or external information, use the web_search tool
                        8. You can combine business data with web search results to provide comprehensive answers

                        IMPORTANT WEB SEARCH RULES:
                        - When user says "scrape this website [URL]", use web_search with search_type='scrape' and query=the exact URL
                        - DO NOT modify URLs or add site: prefixes when scraping
                        - When user provides a specific URL to scrape, use that exact URL as the query
                        - Use search_type='search' only for general web queries, not for specific URLs

                        Always provide specific details from the data rather than generic responses.""",
                ),
                ("user", "{input}"),
                ("assistant", "{agent_scratchpad}"),
            ]
        )

        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True, handle_parsing_errors=True
        )

    def query(self, question: str) -> str:
        try:
            result = self.agent_executor.invoke({"input": question})
            return result["output"]
        except Exception as e:
            return f"Error processing query: {str(e)}"


def create_agent(
    api_key: str,
    azure_endpoint: str,
    deployment_name: str,
    api_version: str = "2024-02-15-preview",
) -> BusinessDataAgent:
    return BusinessDataAgent(api_key, azure_endpoint, deployment_name, api_version)
