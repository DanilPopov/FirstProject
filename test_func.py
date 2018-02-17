#def get_vat(price, vat_rate):
   # vat = int(price) / 100 * int(vat_rate)
  #  price_no_vat = int(price) - vat
 #   print(price_no_vat)


#rice1 = input('Введите цену: ')
#vat_rate1 = input('Введите НДС: ')

#if:
 #   vat_rate1><10, 18
  #  print("Неверный НДС")
#else:
#get_vat(price1, vat_rate1)

def get_summ(one, two, delimeter=' '):
    string = str(one) + str(delimeter) + str(two)
    return string.upper()
print(get_summ('hello,', 'world!'))
