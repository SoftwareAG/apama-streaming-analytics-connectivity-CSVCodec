# Sample PySys testcase
# Copyright (c) 2016 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors. 
# Use, reproduction, transfer, publication or disclosure is prohibited except as specifically provided for in your License Agreement with Software AG 

from pysys.constants import *
from pysys.basetest import BaseTest
from apama.correlator import CorrelatorHelper

class PySysTest(BaseTest):

	def execute(self):
		# since we can't specify locations other than APAMA_WORK/HOME and cwd, 
		# have to copy input file to output dir
		import shutil
		shutil.copyfile(self.input+'/'+'input.txt', self.output+'/'+'input.txt')
		
		# Can specify which port the correlator runs on using '-X CORR_PORT=15903' on the
		# PySys command line else it will be randomly allocated
		correlator = CorrelatorHelper(self, name='testcorrelator', port=self.CORR_PORT if hasattr(self, 'CORR_PORT') else None)
		correlator.start(arguments=['--connectivityConfig', self.input+'/connectivity.yaml'])
		correlator.receive('received.evt', channels=['received'])
		correlator.injectMonitorscript(self.project.APAMA_HOME+'/monitors/ConnectivityPluginsControl.mon')
		correlator.injectMonitorscript(self.project.APAMA_HOME+'/monitors/ConnectivityPlugins.mon')
		correlator.injectMonitorscript('Test.mon')

		# wait until the output is on disk
		self.waitForSignal('received.evt', expr="com")
		self.waitForSignal('output.txt', expr="com")

	def validate(self):
		self.assertGrep('testcorrelator.out', expr=' (ERROR|FATAL) ', contains=False)
		self.assertDiff('received.evt', 'ref-received.evt')
		self.assertDiff('output.txt', 'ref-output.txt')
