"""Job running time statistics for PyPPL"""
# pylint: disable=invalid-name
import sys
from pathlib import Path
import cmdy
from pyppl.plugin import hookimpl
from pyppl.logger import Logger
from pyppl.template import _TemplateFilter

__version__ = "0.0.1"
logger = Logger(name = 'pyppl_jobtime')

@hookimpl
def cliAddCommand(commands):
	commands.jobtime                  = 'Profiling/Ploting job running time.'
	commands.jobtime.wdir             = commands.list.wdir
	commands.jobtime.unit             = 'second' # s/sec/seconds/m/min/minute/minutes/h/hour
	commands.jobtime.unit.desc        = 'The time unit used in reports (second/minute/hour)'
	commands.jobtime.Rscript          = 'Rscript'
	commands.jobtime.Rscript.desc     = 'The Rscript to run R script to plot the figures'
	commands.jobtime.plottype         = 'boxplot' # violin
	commands.jobtime.plottype.desc    = 'The type of plot to generate'
	commands.jobtime.ggs              = dict()
	commands.jobtime.ggs.desc         = 'Extra expressions for ggplot object.'
	commands.jobtime.show             = False
	commands.jobtime.show.desc        = 'Show the table of running times.'
	commands.jobtime.devpars          = dict(height = 2000, width = 2000, res = 300)
	commands.jobtime.devpars.desc     = 'The dimension and resolution of the output figure.'
	commands.jobtime.outfile.required = True
	commands.jobtime.outfile.desc     = 'The output figure file.'
	commands.jobtime.unit.callback    = lambda opt: opt.setValue(opt.value[0])
	commands.jobtime.proc.required    = True
	commands.jobtime.proc.desc        = 'The processes, if tag or suffix not specified, will include all matched processes.'

def _gettimes(workdir):
	logger.info('Collecting running time data in {} ...'.format(workdir.name))
	for jobdir in workdir.glob('*'):
		if not jobdir.is_dir():
			continue
		timefile = jobdir / 'job.time'
		if not timefile.is_file():
			raise ValueError('Pipeline was not running with pyppl_jobtime plugin enabled.')
		yield float(timefile.read_text())

def _timesToRdata(times, unit):
	logger.info('Converting running times into table ...')
	procs = [proc[6:] for proc in sorted(times.keys())] # remove PyPPL.
	# see if all stem names are different
	# i.e.: pBowtie2.tag.xxx, pBWA.tag.xxx, then make it to
	# pBowtie2, pBWA, otherwise keep the tag and suffix if necessary.
	neatprocs = []
	for proc in procs:
		nproc = proc.split('.')[0]
		if any(p.startswith(nproc + '.') for p in procs if p != proc):
			nproc = '.'.join(proc.split('.')[:2])
			if any(p.startswith(nproc + '.') for p in procs if p != proc):
				nproc = proc
		neatprocs.append(nproc)
	ret = ['Process\tRunning Time({})'.format(unit)]
	for i, proc in enumerate(times.keys()):
		nproc = neatprocs[i]
		rtimes = times[proc]
		for rtime in rtimes:
			rtime = rtime if unit == 's' else \
					rtime/60.0 if unit == 'm' else \
					rtime/3600.0
			ret.append('{proc}\t{rtime}'.format(proc = nproc, rtime = rtime))
	return '\n'.join(ret) + '\n'

def _composeRCode(times, opts):
	datastr = _timesToRdata(times, opts.unit)
	logger.info('Composing R code ...')
	rcode = """
require('ggplot2')
apply.ggs = function(p, ggs) {{
	if (is.null(ggs) || length(ggs) == 0)
		return(p)
	funcs = names(ggs)
	for (i in 1:length(funcs)) {{
		if (!is.null(ggs[[i]])) {{
			p = p + do.call(funcs[i], ggs[[i]])
		}}
	}}
	return (p)
}}

datastr = {datastr!r}
conn = textConnection(datastr)
timedata = read.table(conn, header = TRUE, row.names = NULL, sep = "\t", check.names = FALSE)
if ({show}) {{
	print(timedata)
}}
png({outfile!r}, height = {devpars.height!r}, width = {devpars.width!r}, res = {devpars.res!r})
p = ggplot(timedata, aes(x=Process, y=`Running Time({unit})`)) + geom_{plottype}()
apply.ggs(p, {ggs})
dev.off()
""".format(	datastr  = datastr,
			devpars  = opts.devpars,
			outfile  = opts.outfile,
			unit     = opts.unit,
			show     = _TemplateFilter.R(opts.show),
			ggs      = _TemplateFilter.Rlist(opts.ggs),
			plottype = opts.plottype)
	return rcode

def _plotTimes(times, opts):
	rcode = _composeRCode(times, opts)
	logger.info("Plotting results ...")
	cmdy.echo(rcode, _pipe = True) | cmdy.Rscript('-', _exe = opts.Rscript, _fg = True)

@hookimpl
def cliExecCommand(command, opts):
	if command == 'jobtime':
		wdir  = Path(opts.wdir)
		proc  = opts.proc if opts.proc.startswith('PyPPL.') else 'PyPPL.' + opts.proc
		times = {}
		if wdir.joinpath(proc).is_dir():
			times[proc] = _gettimes(wdir / proc)
		else:
			for workdir in wdir.glob(proc + '.*'):
				times[workdir.name] = _gettimes(workdir)
		_plotTimes(times, opts)

@hookimpl
def jobPreRun(job):
	# add hook to save the running time
	# avoid modifying for other jobs
	config = job.config.copy()

	config['preScript']  = '\n'.join([config.get('preScript', ''), 'TIC=$(date +%s.%3N)'])
	config['postScript'] = '\n'.join([
		'echo $(date +%s.%3N) - $TIC | bc > {!r}'.format(str(job.dir / 'job.time')),
		config.get('postScript', '')])
	job.config = config
