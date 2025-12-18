from typing import Dict

from aitrados_broker.utils.broker_aitrados_map import broker_symbol_contracts, broker_full_symbol_contracts


class BrokerMapOp:
    @classmethod
    def get_contracts(cls,gateway_name: str | None = None) -> Dict[str, dict] | None:
        broker_count = len(broker_symbol_contracts)
        if not broker_count:
            return None
        try:
            if broker_count == 1:
                gateway_name = list(broker_symbol_contracts.keys())[0]
            return broker_symbol_contracts[gateway_name]
        except Exception:
            # traceback.format_exc()
            return None

    @classmethod
    def get_contract_dict(cls,full_symbol_or_broker_symbol: str, gateway_name: str = None):
        broker_count = len(broker_full_symbol_contracts)
        if not broker_count:
            return None
        try:
            if broker_count == 1:
                gateway_name = list(broker_full_symbol_contracts.keys())[0]

            if ":" in full_symbol_or_broker_symbol:
                contracts = broker_full_symbol_contracts[gateway_name][full_symbol_or_broker_symbol]
            else:
                contract = broker_symbol_contracts[gateway_name][full_symbol_or_broker_symbol]
                contracts = {full_symbol_or_broker_symbol: contract}
            return contracts
        except Exception:
            # traceback.format_exc()
            return None