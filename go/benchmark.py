from pyscion import *
import time
import csv


PACKET_COUUNT = 1000

def main():
    print('Setting log level')
    set_log_level(0)
    init()
    print('Local Address is %s' % local_address())
    results = []
    for size in range(10, 60000, 1000):
        print(size)
        t0 = time.time()
        send(packet_count=PACKET_COUUNT, size=size)
        t1 = time.time()
        results.append( (size, (t1-t0)/PACKET_COUUNT) )
    with open('/tmp/results.csv', mode='w') as f:
        w = csv.writer(f)
        w.writerow(('size', 'time'))
        for r in results:
            w.writerow(r)


def send(packet_count, size):
    destination = local_address()+':12345'
    p = paths(destination)
    with connect(destination, p[0]) as fd:
        for i in range(packet_count):
            fd.write(b'a'*size)

if __name__ == "__main__":
    main()
