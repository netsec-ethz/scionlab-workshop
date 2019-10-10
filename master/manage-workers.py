#!/usr/bin/env python

import csv
import click
import os
import subprocess

WORKERS_CSV    = './worker_to_ssh.csv'
WRKDIR         = '/tmp/buildbot-workers'


@click.group(chain=True)
@click.option('--ssh/--no-ssh', default=False, help='Create remote workers (using ssh)')
@click.option('--filename', default=WORKERS_CSV, help='CSV file with workers data')
@click.option('--wrkdir', default=WRKDIR, help='Parent directory for worker data dirs')
@click.option('--dry-run', 'prompting', flag_value='dry', help='Only print commands, do not prompt to run')
@click.option('--yes',     'prompting', flag_value='yes', help='Run commands without prompting')
@click.pass_context
def cli(ctx, filename, **kwargs):
    """Manage workers according to a workers.csv file"""
    ctx.ensure_object(dict)
    with open(filename) as f:
        ctx.obj['workers'] = {row[0]: row[1:] for row in csv.reader(f)}
        ctx.obj['args']    = kwargs

def print_and_run(cmds, prompting=None):
    for cmd in cmds:
        click.echo(cmd)
    if not prompting:
        prompting = 'yes' if click.confirm('Run commands?') else 'dry'
    if prompting == 'yes':
        for cmd in cmds:
            click.secho('>>> {}'.format(cmd), fg='blue')
            subprocess.call(cmd, shell=True)

def sshcmd(host, cmd):
    if "'" in cmd: raise ValueError("refusing to escape quotes in \"{}\" (no way I'd get it right)".format(cmd))
    return "ssh {} '{}'".format(host, cmd)

@cli.command()
@click.option('--passwd', prompt='Worker password', envvar='BUILDBOT_WORKERS_PASSWORD', help='Worker password')
@click.option('--master', default='localhost', help='Buildbot master hostname[:port]')
@click.pass_context
def create(ctx, passwd, master):
    wrkdir = ctx.obj['args']['wrkdir']
    ssh    = ctx.obj['args']['ssh']
    c = sshcmd if ssh else lambda h, cmd: cmd

    cmds = []
    if not ssh: cmds.append('mkdir -p "{}"'.format(wrkdir))
    for name, (scion_addr, host) in ctx.obj['workers'].items():
        create = 'buildbot-worker create-worker -f "{mydir}" {master} {name} {passwd}'.format(
            mydir=os.path.join(wrkdir, 'worker-{}'.format(name)),
            master=master,
            name=name,
            passwd=passwd,
        )
        if ssh:
            cmds.append(sshcmd(host, 'mkdir -p "{}"'.format(wrkdir) + ' && ' + create))
        else:
            cmds.append(create)

    print_and_run(cmds, ctx.obj['args']['prompting'])

@cli.command()
@click.pass_context
def start(ctx):
    wrkdir = ctx.obj['args']['wrkdir']
    ssh    = ctx.obj['args']['ssh']
    c = sshcmd if ssh else lambda h, cmd: cmd

    cmds = []
    for name, (scion_addr, host) in ctx.obj['workers'].items():
        cmds.append(c(host, 'buildbot-worker start "{mydir}"'.format(
            mydir=os.path.join(wrkdir, 'worker-{}'.format(name)),
        )))

    print_and_run(cmds, ctx.obj['args']['prompting'])

@cli.command()
@click.pass_context
def stop(ctx):
    wrkdir = ctx.obj['args']['wrkdir']
    ssh    = ctx.obj['args']['ssh']
    c = sshcmd if ssh else lambda h, cmd: cmd

    cmds = []
    for name, (scion_addr, host) in ctx.obj['workers'].items():
        cmds.append(c(host, 'buildbot-worker stop "{mydir}"'.format(
            mydir=os.path.join(wrkdir, 'worker-{}'.format(name)),
        )))

    print_and_run(cmds, ctx.obj['args']['prompting'])


if __name__ == '__main__':
    cli()
