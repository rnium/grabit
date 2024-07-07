import re
taka_sign = '৳'

def common_formatter(raw_price: str):
    price_str = raw_price
    for c in raw_price:
        if not c.isdigit() and c != '.':
            price_str = price_str.replace(c, '')
    p = re.compile(r'(\d+(\.\d*)?|\.\d+)')
    mat = p.search(price_str)
    return float(mat.group())

def bd_price_formatter1(raw_price: str):
    # use case (startech): 66,500৳68,500৳ 
    p_split = raw_price.split(taka_sign)
    price = common_formatter(p_split[0])
    return price

def bd_price_formatter2(raw_price: str):
    taka = raw_price.replace(taka_sign, '').replace(',', '')
    return float(taka)


FORMATTER_MAPPING = {
    'common_formatter': common_formatter,
    'bd_price_formatter1': bd_price_formatter1,
    'bd_price_formatter2': bd_price_formatter2,
}