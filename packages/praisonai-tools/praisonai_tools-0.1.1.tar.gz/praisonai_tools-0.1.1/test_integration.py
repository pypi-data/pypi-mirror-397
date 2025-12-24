"""Integration test: praisonai-tools custom tools with praisonaiagents built-in tools."""

from praisonaiagents import Agent
from praisonaiagents.tools import tavily_search  # Built-in tool
from praisonai_tools import tool  # Custom tool decorator


# Create a custom tool using praisonai-tools
@tool
def summarize_results(text: str, max_length: int = 100) -> str:
    """Summarize text to a shorter version.
    
    Args:
        text: The text to summarize
        max_length: Maximum length of summary
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# Test 1: Use built-in tavily_search tool
print("=" * 60)
print("Test 1: Using built-in tavily_search from praisonaiagents")
print("=" * 60)

agent1 = Agent(
    instructions="You are a research assistant. Use the tavily_search tool to find information.",
    tools=[tavily_search],
    verbose=True
)

result1 = agent1.start("Search for 'Python programming language' and give me a brief summary")
print(f"\nResult: {result1}\n")


# Test 2: Use custom tool from praisonai-tools
print("=" * 60)
print("Test 2: Using custom @tool from praisonai-tools")
print("=" * 60)

agent2 = Agent(
    instructions="You are a text processor. Use the summarize_results tool when asked to summarize.",
    tools=[summarize_results],
    verbose=True
)

result2 = agent2.start("Summarize this text: 'Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.'")
print(f"\nResult: {result2}\n")


# Test 3: Combine built-in and custom tools
print("=" * 60)
print("Test 3: Combining built-in + custom tools")
print("=" * 60)

agent3 = Agent(
    instructions="You are a research assistant. First search for information using tavily_search, then summarize the key findings.",
    tools=[tavily_search, summarize_results],
    verbose=True
)

result3 = agent3.start("Search for 'machine learning basics' and summarize what you find")
print(f"\nResult: {result3}\n")

print("=" * 60)
print("All tests completed!")
print("=" * 60)
