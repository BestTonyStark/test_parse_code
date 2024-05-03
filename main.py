#!!! файл jsonfile.json должен находиться в одной директории с main.py
import requests
from bs4 import BeautifulSoup
import re
import json

page = 1


# В списке всех товаров нет информации о бренде каждого товара, поэтому находим бренд на странице самого товара
def parse_brand(link):
    url = str(link)
    req = requests.get(url)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    brand = (
        soup.find("span", string=re.compile("Бренд"))
        .find_parent()
        .find_next()
        .find_next()
        .find_next()
        .find_next()
        .text
    )
    return brand.split()


# Создаем цикл, что бы перелистывать страницы
while True:
    url = (
        "https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe"
        + "?page="
        + str(page)
    )
    req = requests.get(url)
    src = req.text
    soup = BeautifulSoup(src, "lxml")

    kofes = soup.find("div", id="products-inner").find_all(
        "div",
        class_="catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop",
    )
    # Проверяему на наличие объектов в наличии на странице, что бы завершить цикл while, когда нацнуться пустые страницы
    if kofes:
        for kofe in kofes:
            price = kofe.find(
                "span",
                class_="product-price nowrap product-unit-prices__actual style--catalog-2-level-product-card-major-actual",
            )
            if price:
                promo_price = price.find(
                    "span", class_="product-price__sum-rubles"
                ).text
                regular_price = promo_price
            else:
                promo_price = (
                    kofe.find(
                        "span",
                        class_="product-price nowrap product-unit-prices__actual style--catalog-2-level-product-card-major-actual color--red",
                    )
                    .find("span", class_="product-price__sum-rubles")
                    .text
                )
                price = kofe.find(
                    "span",
                    class_="product-price nowrap product-unit-prices__old style--catalog-2-level-product-card-major-old",
                )
                if price:
                    regular_price = price.find(
                        "span", class_="product-price__sum-rubles"
                    ).text
            product_id = kofe["id"]
            name = kofe.find("span", class_="product-card-name__text").text.strip()
            href_product = "https://online.metro-cc.ru" + kofe.find("a")["href"]
            brand = parse_brand(href_product)
            # Словарь со всей информацией о товаре
            product_info = {
                "id": product_id,
                "name": name,
                "link": href_product,
                "regular_price": regular_price,
                "promo_price": promo_price,
                "brand": brand,
            }
            # Сохраняем в json файл
            with open("jsonfile.json", encoding="utf8") as json_file:
                data = json.load(json_file)
                data["products"].append(product_info)
                with open("jsonfile.json", "w", encoding="utf8") as out_file:
                    json.dump(data, out_file, ensure_ascii=False, indent=4)
    else:
        break
    page += 1
