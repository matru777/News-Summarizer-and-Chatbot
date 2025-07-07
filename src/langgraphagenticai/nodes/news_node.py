from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate



    
class NewsNode:
    def __init__(self, llm):
        self.tavily = TavilyClient()
        self.llm = llm
        self.state = {}

    def fetch_news(self, state: dict) -> dict:
        frequency = state['messages'][0].content.lower()
        genre = state.get('genre', 'general').lower()

        self.state['frequency'] = frequency
        self.state['genre'] = genre

        time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}

        query = f"Summarize the latest {genre} news from global and Indian sources."

        response = self.tavily.search(
            query=query,
            topic="news",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=10,
            days=days_map[frequency],
        )

        state['news_data'] = response.get('results', [])
        self.state['news_data'] = state['news_data']
        return state

    def summarize_news(self, state: dict) -> dict:
        news_items = self.state['news_data']

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Summarize the news articles into markdown format. For each item include:
            - Date in **YYYY-MM-DD** format in IST timezone
            - Concise sentences summary from latest news
            - Sort news by date wise (latest first)
            - Source URL as link
            Use format:
            ### [Date]
            - [Summary](URL)"""),
            ("user", "Articles:\n{articles}")
        ])

        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
            for item in news_items
        ])

        response = self.llm.invoke(prompt_template.format(articles=articles_str))
        state['summary'] = response.content
        self.state['summary'] = state['summary']
        return self.state

    def save_result(self, state):
        frequency = self.state['frequency']
        genre = self.state.get("genre", "general")
        summary = self.state['summary']

        filename = f"./News/{genre}_{frequency}_summary.md"

        with open(filename, 'w', encoding="utf-8") as f:
            f.write(f"# {genre.capitalize()} - {frequency.capitalize()} News Summary\n\n")
            f.write(summary)

        self.state['filename'] = filename
        return self.state