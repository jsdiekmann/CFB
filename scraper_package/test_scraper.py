# import teamnames
# from bs4 import BeautifulSoup
# import pandas as pd
# import requests



# ppd_url = "https://bcftoys.com/2025-ppd"
# ppd_page = requests.get(ppd_url).text
# ppd_soup = BeautifulSoup(ppd_page, "html.parser")

# ppd_titles_obj = ppd_soup.table.tr.next_sibling
# ppd_titles = [title.text for title in ppd_titles_obj]
# ppd_df = pd.DataFrame(columns = ppd_titles)
# ppd_column_data = [line for line in ppd_soup.table.find_all('tr') if len(line.find_all('strong')) == 0]

# for row in ppd_column_data[1:]:
#     row_data = row.find_all('td')
#     row_data_info = [info.text.strip() for info in row_data]
    
#     length = len(ppd_df)
#     ppd_df.loc[length] = row_data_info

# ppd_df['OPD'] = pd.to_numeric(ppd_df['OPD'])
# ppd_df['DPD'] = pd.to_numeric(ppd_df['DPD'])
# ppd_df['Team'] = ppd_df['Team'].replace(teamnames.name_map)

# print(ppd_df)
