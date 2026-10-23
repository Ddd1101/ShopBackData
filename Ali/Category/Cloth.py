"""1688 童装品类适配器：多尺码（颜色 + 尺码）聚合。"""

from ...Common.Model import BeihuoItem, SizeItem, CATEGORY_CLOTH
from ...Common.Utils.PriceUtil import CalCargoNum4ERP, CalPriceColByName
from .Base import CategoryAdapter


class ClothCategoryAdapter(CategoryAdapter):
    category_key = CATEGORY_CLOTH

    def get_price(self, cargo_number, sku_value, col_num=0):
        worksheet = self._load_grid()
        row_index = -1
        for t in range(1, worksheet.nrows):
            value = worksheet.cell(t, col_num).value
            if isinstance(value, (int, float)):
                value = int(value)
            if str(cargo_number) == str(value):
                row_index = t
                break
        if row_index == -1:
            self.logger.debug('%s ： 未找到对应货号1', cargo_number)
            return 0
        col_index = CalPriceColByName(sku_value, worksheet)
        if col_index != -1:
            price = worksheet.cell(row_index, int(col_index)).value
        else:
            price = ''
        if price == '':
            self.missing_price_records.append(
                '货号：' + str(cargo_number) + ' 规格：' + str(sku_value)
            )
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
                cargo_number = product_item[cargo_number_tag]
                color = product_item['skuInfos'][0]['value']
                height = product_item['skuInfos'][1]['value']

                cargo_number = cargo_number.split('【')[-1]
                cargo_number = CalCargoNum4ERP(cargo_number)

                product_dict = beihuo.setdefault(cargo_number, {}).setdefault(
                    color,
                    {'products': {}, 'productImgUrl': product_item['productImgUrl'][1]},
                )
                product_dict['products'].setdefault(height, {'quantity': 0})
                product_dict['products'][height]['quantity'] += product_item['quantity']
                product_dict['products'][height]['price'] = self.get_price(cargo_number, height)
                product_dict['products'][height]['cost'] = (
                    product_dict['products'][height]['price']
                    * product_dict['products'][height]['quantity']
                )

        items = []
        for cargo_number, colors in beihuo.items():
            for color, bucket in colors.items():
                sizes = []
                for height, info in sorted(bucket['products'].items()):
                    sizes.append(SizeItem(
                        size=height,
                        quantity=info['quantity'],
                        price=info['price'],
                        cost=info['cost'],
                    ))
                total_qty = sum(s.quantity for s in sizes)
                total_cost = sum(s.cost for s in sizes)
                items.append(BeihuoItem(
                    cargo_number=cargo_number,
                    color=color,
                    product_img_url=bucket['productImgUrl'],
                    quantity=total_qty,
                    price=0.0,
                    cost=total_cost,
                    sizes=sizes,
                ))
        return items