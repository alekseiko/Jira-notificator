#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import SOAPpy
import subprocess
import sys
import config

ISSUES_FOR_REVIEW = "project = {0} AND assignee = currentUser() AND status = 'To Be Reviewed'" 
ISSUES_FOR_ACCEPT = "project = {0} AND status = 'To Be Accepted'" 

class JiraEngine: 

	def __init__(self, login, password, url, \
			resultCount = config.resultCount):
		self.__login = login
		self.__password = password
		self.__url = url
		self.__resultCount = resultCount

	def __getIssuesByJQL(self, jql):

		client, auth = self.__initJiraClient()

		return [(issue["key"], issue["summary"]) \
			for issue in client.getIssuesFromJqlSearch(auth, \
				jql, self.__resultCount)]

	def get_issues_for_review(self, project = config.project):
		return self.__getIssuesByJQL(ISSUES_FOR_REVIEW.format(project))
	
	def get_issues_for_accept(self, project = config.project):
		return self.__getIssuesByJQL(ISSUES_FOR_ACCEPT.format(project))


	def __initJiraClient(self):
		client = SOAPpy.SOAPProxy(self.__url)
		auth = client.login(self.__login, self.__password)
		return client, auth
		
def execCmd (command, home = config.home):
	proc = subprocess.Popen(command, cwd = home, \
				 stderr = subprocess.PIPE, \
				 stdout = subprocess.PIPE, \
				 shell = True)
	try:
		stdout_value = proc.stdout.read().rstrip()
		stderr_value = proc.stderr.read().rstrip()
		status = proc.wait()
	finally:
		proc.stdout.close()
		proc.stderr.close()

#                if status != 0:

	return stdout_value

def send (header, issues):
	# if list of issues is not empty	
	if issues:
		command = "notify-send '%s' '" % header
		for (key, desc) in issues:
			command += "[%s] %s " % (key, desc)
		command +="'"
		execCmd(command)

def main ():
	jira = JiraEngine(config.jiraLogin, config.jiraPassword, config.jiraEndpoint)
	send("Accept to master", jira.get_issues_for_accept())
	send("Need to review", jira.get_issues_for_review())

if __name__ == "__main__":
	main()	
