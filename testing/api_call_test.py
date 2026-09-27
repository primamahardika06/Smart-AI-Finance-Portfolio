# import requests
# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()

# api = os.getenv("SECTOR_API_KEY")

# url = "https://api.sectors.app/v2/company/report/BBCA/"

# headers = {"Authorization": api}

# response = requests.get(url, headers=headers)

# result = json.loads(response.text)

# historical_list = result.get('valuation', {}).get('historical_valuation', [])
# ratio_list = result.get('financials',{}).get('historical_financial_ratio', [])
# future_list = result.get('future', {}).get('company_growth_forecasts', [])

# template_result = {
#     "symbol": result.get('symbol'),
#     "company_name": result.get('company_name'),
#     "sector": result['overview'].get('sector'),
#     "pe_ratio": historical_list[0].get('pe'),
#     "pbv": historical_list[0].get('pb'),
#     "roe": ratio_list[0].get('profitability', {}).get('roe', 'N/A'),
#     "revenue_growth": future_list[0].get('revenue_growth')
# }

# print(json.dumps(template_result, indent=4))