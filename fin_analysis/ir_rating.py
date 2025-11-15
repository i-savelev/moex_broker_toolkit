from bs4 import BeautifulSoup
import pandas as pd

class IRrating:
    def __init__(self, path:str):
        self.path = path
        self.data:pd.DataFrame = self._rating_table()

    def _rating_table(self):
        data = []
        file_path = self.path 
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.select_one('.my_table_body')
        if not body:
            raise ValueError("Не найден блок с телом таблицы (.my_table_body)")
        rows = soup.find_all("div", class_="my_table_tr_left")
        for row in rows:
            comp = {}
            name_div = row.find("div", class_="tr_item_ir_issuer")
            name = name_div.find('span').text
            rating_div = row.find("div", class_="tr_item_ir_rating_mob")
            rating = rating_div.find('span').text
            comp['name'] = name
            comp['rating'] = rating
            data.append(comp)
            # print(f'name={name}; rating={rating}')
        return pd.DataFrame(data).set_index('name')
    
    def get_rating(self, name:str):
        for key in self.data.keys():
            words = key.split(' ')
            for word in words:
                if len(word)>1 and word.lower() in name.lower(): 
                    print(word.lower(), name.lower())
                    return float(self.data[key])
            
if __name__ == '__main__':
    ir = IRrating('fin_metrics/IR-рейтинг компаний.html')
    print(ir.get_rating('ТМК (TRMK)'))
    # print(ir.data)
