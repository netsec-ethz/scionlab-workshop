from pyscion import *


def main():
    print('Setting log level')
    set_log_level(1)
    init()
    print('Local Address is %s' % local_address())

    destination = '17-ffaa:1:a,[127.0.0.1]:12345'
    p = paths(destination)
    print('Got %d paths:' % len(p))
    for i in range(len(p)):
        print('[%d] %s' % (i, str(p)))

    fd = connect(destination, p[0])
    write(fd, b'abcd')
    close(fd)

    fd = listen(11223)
    buffer = bytearray(4096)
    client_address, n = read(fd, buffer)
    print('Read from %s an amount of %d bytes' % (client_address, len(buffer[:n])))
    print('buffer is:', buffer[:n])


if __name__ == "__main__":
    main()
