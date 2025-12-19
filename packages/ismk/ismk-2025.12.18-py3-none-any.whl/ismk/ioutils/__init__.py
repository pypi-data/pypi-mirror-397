from ismk.ioutils.branch import branch
from ismk.ioutils.collect import collect
from ismk.ioutils.evaluate import evaluate
from ismk.ioutils.exists import exists
from ismk.ioutils.lookup import lookup
from ismk.ioutils.rule_items_proxy import rule_item_factory
from ismk.ioutils.subpath import subpath
from ismk.ioutils.input import parse_input, extract_checksum, flatten


def register_in_globals(_globals):
    _globals.update(
        {
            "lookup": lookup,
            "evaluate": evaluate,
            "branch": branch,
            "collect": collect,
            "exists": exists,
            "input": rule_item_factory("input"),
            "output": rule_item_factory("output"),
            "params": rule_item_factory("params"),
            "resources": rule_item_factory("resources"),
            "threads": rule_item_factory("threads"),
            "subpath": subpath,
            "parse_input": parse_input,
            "extract_checksum": extract_checksum,
            "flatten": flatten,
        }
    )
