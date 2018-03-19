from fabric.api import *
import os
import sys
import string
import time
# Custom Code Enigma modules
import common.Utils
import Drupal

# Override the shell env variable in Fabric, so that we don't see 
# pesky 'stdin is not a tty' messages when using sudo
env.shell = '/bin/bash -c'


@task
def main(shortname, branch, command, backup=True):
  with settings(warn_only=True):
    if run('drush sa | grep ^@%s_%s$ > /dev/null' % (shortname, branch)).failed:
      raise SystemError("You can't run a command on a site that doesn't exist! Alias @%s_%s not recognised." % (shortname, branch))

  # Take a database backup first if told to.  
  if backup:
    db_name = Drupal.get_db_name(shortname, branch, "default")
    execute(common.MySQL.mysql_backup_db, db_name, 'drush_command', True)

  # Strip nastiness from the command
  command = command.replace(";", "")
  command = command.replace("&&", "")
  command = command.replace("&", "")
  command = command.replace("||", "")
  command = command.replace("|", "")
  command = command.replace("!", "")
  command = command.replace("<", "")
  command = command.replace(">", "")

  print "Command is drush @%s_%s %s" % (shortname, branch, command)

  BLACKLISTED_CMDS = ['sql-drop', 'site-install', 'si', 'sudo', 'rm', 'shutdown', 'reboot', 'halt', 'chown', 'chmod', 'cp', 'mv', 'nohup', 'echo', 'cat', 'tee', 'php-eval', 'variable-set', 'vset']
  blacklisted = False
  blacklisted = common.Utils.detect_malicious_strings(BLACKLISTED_CMDS, cmd)
  if blacklisted:
    raise SystemError("Surely you jest... I won't run drush @%s_%s %s. Ask a sysadmin instead." % (shortname, branch, command))

  run("drush -y @%s_%s %s" % (shortname, branch, command) )
