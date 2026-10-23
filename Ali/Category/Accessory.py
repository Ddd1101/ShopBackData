"""1688 饰品类适配器：单品（无尺码）聚合。"""

from ...Common.Model import BeihuoItem, CATEGORY_ACCESSORY
from .Base import CategoryAdapter


class AccessoryCategoryAdapter(CategoryAdapter):
    category_key = CATEGORY_ACCESSORY

    def get_price(self, cargo_number, sku_value, col_num=0):
        worksheet = self._load_grid()
        row_index = -1
        for t in range(1, worksheet.nrows):
            if str(cargo_number) == str(worksheet.cell(t, col_num).value):
                row_index = t
                break
        if row_index == -1:
            self.logger.debug('%s ： 未找到对应货号2', cargo_number)
            return 0
        price = worksheet.cell(row_index, 2).value
        if price == '':
            price = 0
        return float(price)

    def aggregate(self, orders, mode=0):
        beihuo = {}
        for order in orders:
            self.check_cancel()
            base_info = order['baseInfo']
            if mode != 0 and (
                'sellerRemarkIcon' not in base_info
                or base_info['sellerRemarkIcon'] != str(mode)
            ):
                continue
            if 'sellerRemarkIcon' in base_info and base_info['sellerRemarkIcon'] in ('2', '3'):
                continue

            for product_item in order['productItems']:
                if 'refund' in product_item and product_item['refund'] > 0:
                    continue

                cargo_number_tag = (
                    'cargoNumber' if 'cargoNumber' in product_item else 'productCargoNumber'
                )
                cargo_number = ''
                if cargo_number_tag in product_item:
                    cargo_number = product_item[cargo_number_tag]

                if 'skuInfos' not in product_item:
                    color = '无sku'
                else:
                    color = product_item['skuInfos'][0]['value']

                item = beihuo.setdefault(cargo_number, {
                    'color': color,
                    'quantity': 0,
                    'price': self.get_price(cargo_number, color),
                    'productImgUrl': product_item['productImgUrl'][1],
                })
                item['quantity'] += product_item['quantity']
                item['cost'] = item['price'] * item['quantity']

        items = []
        for cargo_number, info in beihuo.items():
            items.append(BeihuoItem(
                cargo_number=cargo_number,
                color=info['color'],
                quantity=info['quantity'],
                price=info['price'],
                cost=info['cost'],
                product_img_url=info['productImgUrl'],
            ))
        return items