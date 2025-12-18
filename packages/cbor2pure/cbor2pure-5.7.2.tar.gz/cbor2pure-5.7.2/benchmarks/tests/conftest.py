import json
from collections import namedtuple
from operator import attrgetter

from cbor2pure import dumps as pydumps
from cbor2pure import loads as pyloads

Contender = namedtuple("Contender", "name,dumps,loads")

contenders = []

contenders.append(Contender("json", json.dumps, json.loads))
contenders.append(Contender("cbor2pure", pydumps, pyloads))


# See https://github.com/pytest-dev/pytest-cov/issues/418
def pytest_configure(config):
    cov = config.pluginmanager.get_plugin("_cov")
    cov.options.no_cov = True
    if cov.cov_controller:
        cov.cov_controller.pause()


# See https://github.com/ionelmc/pytest-benchmark/issues/48


def pytest_benchmark_group_stats(config, benchmarks, group_by):
    result = {}
    for bench in benchmarks:
        engine, data_kind = bench["param"].split("-")
        group = result.setdefault("{}: {}".format(data_kind, bench["group"]), [])
        group.append(bench)
    return sorted(result.items())


def pytest_generate_tests(metafunc):
    if "contender" in metafunc.fixturenames:
        metafunc.parametrize("contender", contenders, ids=attrgetter("name"))
