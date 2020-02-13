from pyscion import *


def main():
    print('Setting log level')
    set_log_level(1)
    init()
    print('Local Address is %s' % local_address())

    destination = '17-ffaa:1:a,[127.0.0.1]:12345'
    p = get_paths(destination, loop_till_have_paths=False)
    print('Got %d paths:' % len(p))
    for i in range(len(p)):
        print('[%d] %s' % (i, str(p)))

    fd = connect(destination, p[0])
    fd.write(b'abcd')
    fd.close()

    with connect(destination, p[0]) as fd:
        fd.write(b'zzzz')

    buffer = bytearray(4096)
    fd = listen(11223)
    client_address, n = fd.read(buffer)
    print('Read from %s an amount of %d bytes' % (client_address, len(buffer[:n])))
    print('buffer is:', buffer[:n])
    fd.close()

    with listen(11223) as fd:
        client_address, n = fd.read(buffer)
    print('Read from %s an amount of %d bytes' % (client_address, len(buffer[:n])))
    print('buffer is:', buffer[:n])


if __name__ == "__main__":
    main()
