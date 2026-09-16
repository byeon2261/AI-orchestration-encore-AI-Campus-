import math
from math import sqrt
import urllib.parse as url_tools
from urllib.parse import urlparse as parse_url

address = "https://example.com/books?page=2"
print("1) 모듈 이름으로 제곱근:", math.sqrt(81))
print("2) 함수 이름으로 제곱근:", sqrt(81))
print("3) 별명으로 주소 경로:", url_tools.urlparse(address))
print("4) 함수 별명으로 검색 조건:", parse_url(address).query)