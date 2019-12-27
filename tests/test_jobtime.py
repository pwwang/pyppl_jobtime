import sys
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
	sys.argv[1:] = ['jobtime', '--wdir', str(tmp_path), '--proc', 'pJobTime', '--outfile', str(tmp_path/'jobtime.png')]
	console.main()