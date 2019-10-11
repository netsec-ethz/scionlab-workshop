import pyscion as sci
import sys
import time


MTU = 1300  # leave enough space for SCION headers


def main():
    sci.init()
    print('Local Address is {}'.format(sci.local_address()))
    for dest_addr, nbytes in parse_tasks_from_stdin():
        destination = "{}:12345".format(dest_addr) # send to port 12345
        print(' === TASK to destination {} : {}MB ==='.format(destination, int(nbytes/1024/1024)))
        paths = really_get_paths(destination)
        print('Got %d paths' % len(paths))
        with sci.connect(destination, paths[0]) as fd:
            for i in range(int(nbytes / 1000)+1):
                fd.write(MTU*b'a')


def really_get_paths(destination):
    # getting paths is async, so let's just retry until we get some
    while True:
        try:
            return sci.paths(destination)
        except sci.SCIONException:
            time.sleep(0.1)


def parse_tasks_from_stdin():
    def parse_line(line):
        dest, nbytes = line.split()
        return dest, int(nbytes)
    return [parse_line(line) for line in sys.stdin]


if __name__ == "__main__":
    main()
