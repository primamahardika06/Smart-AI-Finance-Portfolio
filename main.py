from typing import TypedDict, Annotated, Sequence, List
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import streamlit as st
import requests
import os
import json

load_dotenv()


class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages]
    stock_list : List[str]
    
@tool
def get_company_performance(ticker: str) -> str: 
    """Use this tool to evaluate whether a specific Indonesian (IDX) stock is financially healthy for portfolio inclusion. It analyzes fundamental metrics from the Sectors API, such as profitability, debt levels, and valuation. Input must be a valid stock ticker symbol (e.g., 'BBCA')."""
    
    mode = os.getenv("MODE")
    
    if mode == "TESTING":
        with open("data/mock-sector.json", 'r') as f:
            data = json.load(f)
    else:
        return "Akan melakukan request API asli"
    
    hasil = data.get(ticker)
    
    if not hasil:
        return f"Data untuk ticker {ticker} tidak ditemukan dalam database."
    
    template_result = {
        "Symbol":hasil['symbol'],
        "Company_name":hasil['company_name'],
        "Sector":hasil['sector'],
        "PE Ratio":hasil['pe_ratio'],
        "PBV":hasil['pbv'],
        "ROE":hasil['roe'],
        "Revenue growth":hasil['revenue_growth']
    }
    
    return str(template_result)

tools = [get_company_performance]
llm = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    temperature= 0.0
).bind_tools(tools)

def agen_node(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="""
    You are an expert Financial Analyst AI specialized in the Indonesian Stock Market (IDX). Your primary objective is to analyze stock portfolios, evaluate financial health, and provide data-driven investment insights.

    You operate within a system where all financial data, stock prices, company fundamentals, and market news are strictly provided to you by the Sectors API. 

    CORE RULES & CONSTRAINTS:
    1. STRICT DATA RELIANCE: You must base your entire analysis ONLY on the raw data (JSON/text) provided in the user prompt. 
    2. NO HALLUCINATION: DO NOT invent, guess, or pull external financial figures, historical prices, or news that are not present in the provided data. If a metric is missing, explicitly state: "Data for [metric] is not available in the current Sectors API context."
    3. OBJECTIVITY: Provide unbiased, analytical, and professional insights. Focus on fundamental analysis, valuation, and trend identification.
    4. DISCLAIMER: Always maintain a professional boundary. Remind the user that your analysis is for informational purposes and does not constitute direct financial advice.

    WORKFLOW INSTRUCTIONS:
    When receiving a user query and the accompanying Sectors API data:
    - Step 1: Digest the provided financial metrics (e.g., Revenue, Net Income, P/E Ratio, PBV).
    - Step 2: Compare the metrics against industry standards or historical performance if the data allows.
    - Step 3: Identify key strengths (bullish factors) and weaknesses/risks (bearish factors) from the data.
    - Step 4: Synthesize a clear, actionable summary.

    OUTPUT FORMAT:
    Unless the user specifies otherwise, structure your analysis using Markdown with the following sections:
    - 📊 Executive Summary (Brief overview of the stock/portfolio health)
    - 📈 Fundamental Analysis (Breakdown of key metrics provided)
    - ⚠️ Risk Factors (Potential downsides based on the data)
    - 💡 Conclusion (Final objective thought)

    [SYSTEM CONTEXT ENDS HERE. AWAITING USER QUERY AND SECTORS DATA]
        
    """)
    
    if not state["messages"]:
        print("\nAI: I'm ready to be your smart portofolio rebalancing assistant ")
        
    
    all_message = [system_prompt] + list(state['messages'])
    response = llm.invoke(all_message)
    
    return {"messages": [response]}

builder = StateGraph(AgentState)

builder.add_node("agent", agen_node)
tool_node = ToolNode(tools=tools) 
builder.add_node("tools", tool_node)
builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    tools_condition
)

builder.add_edge("tools", "agent")

graph = builder.compile()


if __name__ == "__main__":
    # user = input("\nUSER: ")
    initial_state = {
        "messages": [
            HumanMessage(content="Tolong analisis kesehatan finansial saham BBCA untuk portofolio saya.")
        ]
    }
    
    print("🤖 Memulai AI Agent Smart Portfolio Rebalancing...")
    print("-" * 50)
    
    result = graph.invoke(initial_state)
    
    print("\n--- HASIL EKSEKUSI AGEN ---")
    for message in result["messages"]:
        if isinstance(message, HumanMessage):
            print(f"\n👤 USER:\n{message.content}")
        elif isinstance(message, AIMessage):
            if isinstance(message.content, list):
                for item in message.content:
                    if isinstance(item, dict) and 'text' in item:    
                        print(f"\n🤖 AI AGENT:\n{item['text']}")
        elif isinstance(message, ToolMessage):
            print(f"\n⚙️ [TOOL RESPONSE - SECTORS API MOCK]:\n{message.content}")