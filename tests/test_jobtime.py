import sys
from pathlib import Path
import cmdy
import pytest
import pyppl_jobtime
from pyppl import config_plugins, Proc, PyPPL
config_plugins(pyppl_jobtime)
from pyppl import console

def test_jobtime(tmp_path):

	pJobTime = Proc(
		forks = 5, ppldir = tmp_path,
		input = {'a':[.5,.8,1.2,1.7,2]},
		output = 'a:1', script = 'sleep {{i.a}}')
	PyPPL().start(pJobTime).run()
	sys.argv = ['pyppl', 'jobtime', '--wdir', str(tmp_path), '--proc', 'pJobTime', '--outfile', str(tmp_path/'jobtime.png')]
	console.main()

@pytest.mark.parametrize('string,rdata, ignoreintkey', [
	(True, 'TRUE', True),
	(False, 'FALSE', True),
	(None, 'NULL', True),
	('inf', 'Inf', True),
	('-Inf', '-Inf', True),
	('true', 'TRUE', True),
	('false', 'FALSE', True),
	('na', 'NA', True),
	('null', 'NULL', True),
	('abc', "'abc'", True),
	('r:1', '1', True),
	(Path('.'), "'.'", True),
	([1,2,3], "c(1,2,3)", True),
	({'a':1}, "list(`a`=1)", True),
	({0:1}, "list(1)", True),
	({0:1}, "list(`0`=1)", False),
])
def test_to_r(string, rdata, ignoreintkey):
	assert pyppl_jobtime._to_r(string, ignoreintkey) == rdata
