import re

from vnpy.trader.constant import Exchange, Product
from vnpy.trader.object import ContractData


class FullSymbolGenerator:
    @classmethod
    def crypto(cls, broker_original_symbol:str,contract: ContractData, provider=None)->ContractData:
        full_symbol = "CRYPTO:GLOBAL:"
        arr = str.split(broker_original_symbol, "_")

        symbol = arr[0]
        symbol = symbol.replace("-", "")
        symbol = symbol.upper()
        #USDT,USDC replace USD
        if symbol.endswith("USDT") or symbol.endswith("USDC"):
            symbol = symbol[:-4] + "USD"

        full_symbol=(full_symbol+symbol).upper()
        contract.full_symbol=full_symbol
        contract.underlying_name=symbol.upper()
        return contract

    @classmethod
    def mt5(cls, broker_data: dict,contract: ContractData, provider=None) -> str | None:
        #{'symbol': 'AUDCAD', 'digits': 5, 'lot_size': 100000.0, 'min_lot': 0.01, 'path': 'Forex\\AUDCAD', 'category': None}
        symbol = broker_data['symbol']
        symbol_path=broker_data['path'].upper()
        full_symbol=None
        if symbol_path.startswith("FOREX\\"):
            full_symbol = "FOREX:GLOBAL:"
        elif symbol_path.startswith("NASDAQ\\"):
            full_symbol=f"STOCK:US:"
        if full_symbol:
            full_symbol = (full_symbol + symbol).upper()
            contract.full_symbol = full_symbol
            contract.underlying_name = symbol.upper()


    @classmethod
    def ctp(cls, contract:ContractData)->ContractData:
        if contract.product not in [Product.FUTURES,Product.OPTION]:
            return None
        symbol = contract.symbol.replace("-", "")
        symbol = symbol.replace("_", "")
        symbol = symbol.upper()

        if contract.option_underlying:


            full_symbol = "OPTION:CN:"
        else:
            full_symbol = "FUTURE:CN:"

        if contract.exchange == Exchange.CZCE:
            symbol = cls._fix_czce_code(symbol)

        underlying_name=None
        if full_symbol == "OPTION:CN:":
            # P2609C9200 -> P2609250707C9200
            # 其中 P2609 是期货合约,250707 是期权到期日(2025年7月7日)
            if contract.option_expiry:
                # 将到期日转换为 YYMMDD 格式
                expiry_date = contract.option_expiry.strftime("%y%m%d")

                # 查找 C 或 P 的位置(期权类型标识)
                option_type_pos = -1
                for i, char in enumerate(symbol):
                    if char in ['C', 'P'] and i > 0:
                        # 确保前一个字符是数字
                        if symbol[i - 1].isdigit():
                            option_type_pos = i
                            break
                future_symbol=symbol[:option_type_pos]
                if contract.exchange == Exchange.CZCE:
                    future_symbol = cls._fix_czce_code(future_symbol)
                underlying_name = future_symbol[:-4]
                if option_type_pos > 0:
                    # 在 C/P 前插入到期日
                    symbol = future_symbol +'.'+ expiry_date + symbol[option_type_pos:]
        else:
            underlying_name = symbol[:-4]
        full_symbol=(full_symbol+symbol).upper()
        contract.full_symbol=full_symbol
        contract.underlying_name=underlying_name.upper()
        return contract



    @classmethod
    def _fix_czce_code(cls, symbol: str) -> str:
        """
        Fix missing year digits in CZCE contract codes

        Rules:
        - AP601 -> AP2601 (January 2026)
        - TA601C4350 -> TA2601C4350 (January 2026 call option)

        CZCE contract encoding rule: commodity code + year/month + option info
        When there are only 3 digits, usually missing the tens digit of year, default add 2
        """
        # Match pattern: letters + 3 digits + optional option part
        match = re.match(r'^([A-Z]+)(\d{3})(.*)', symbol)
        if not match:
            return symbol

        commodity_code = match.group(1)  # Commodity code: AP, TA, etc.
        three_digits = match.group(2)  # 3 digits: 601
        option_part = match.group(3)  # Option part: C4350 or empty

        # Check if correction is needed (first digit > 2 indicates possible missing year tens digit)
        first_digit = int(three_digits[0])

        if first_digit >= 3:  # 6 in 601 indicates year 26, missing tens digit 2
            # Add 2 before the 3 digits
            fixed_code = commodity_code + "2" + three_digits + option_part
        else:
            # Digits are reasonable, no correction needed
            fixed_code = symbol

        return fixed_code
