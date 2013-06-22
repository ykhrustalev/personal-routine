#!/usr/bin/env python
# coding=utf-8

"""
Helpers for currency tax calculation for moedelo.org
"""
import argparse
from xml.dom import minidom

import requests


# date format dd/mm/YYYY
currency_url = "http://www.cbr.ru/scripts/XML_daily.asp?date_req={date}"


def get_currency_rate(date, currency):
    r = requests.get(currency_url.format(date=date))
    assert r.status_code == 200

    dom = minidom.parseString(r.text.encode('ascii', 'ignore'))
    root = dom.getElementsByTagName("ValCurs")[0]

    for node in root.getElementsByTagName("Valute"):
        code = node.getElementsByTagName("CharCode")[0].firstChild.nodeValue
        if code.upper() == currency.upper():
            value = node.getElementsByTagName("Value")[0].firstChild.nodeValue
            return float(value.replace(',', '.'))

    assert False, "{0} rate for {1} not found".format(currency, date)


def format_decimal(value, precision=4):
    template = "{{0:.{0}f}}".format(precision)
    return template.format(value).replace('.', ',')


def format_date(date):
    return date.replace('/', '.').replace('-', '.')


def get_description(payment, rate, currency):
    return "Получение валютной выручки {0} {1} Курс ЦБ {2} руб.".format(
        payment, currency.upper(), format_decimal(rate))


def get_description_rate_change(diff, rate):
    return "Курсовая разница при конвертации по курсу ЦБ РФ {0} на сумму {1}".format(
        format_decimal(rate), format_decimal(diff, 2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process tax conversions\n"
                    "Example:\n"
                    " {0} --payment 1000 --date 21.05.2013".format(__file__))

    parser.add_argument("--payment", required=True,
                        type=int, dest="payment",
                        help="Transaction sum")

    parser.add_argument("--date", required=True,
                        type=str, dest="date",
                        help="Date transit account transaction")

    parser.add_argument("--tc_date",
                        type=str, dest="tc_date", default="",
                        help="Date transit->current accounts transaction")

    parser.add_argument("--currency",
                        type=str, dest="currency", default="USD",
                        help="Transaction currency")

    args = parser.parse_args()

    rate = get_currency_rate(args.date, args.currency)
    text = "Поступление: \n"\
           " Сумма: {1}\n"\
           " Дата: {0}\n"\
           " Описание: {2}\n".format(
        format_date(args.date),
        format_decimal(args.payment * rate, 2),
        get_description(args.payment, rate, args.currency)
    )

    print text

    if args.tc_date:
        tc_rate = get_currency_rate(args.tc_date, args.currency)
        if tc_rate > rate:
            diff = args.payment * (tc_rate - rate)
            text = "Курсовая разница:\n"\
                   " Сумма: {1}\n"\
                   " Дата: {0}\n"\
                   " Описание: {2}\n".format(
                format_date(args.tc_date),
                format_decimal(diff, 2),
                get_description_rate_change(diff, tc_rate)
            )
            print text
