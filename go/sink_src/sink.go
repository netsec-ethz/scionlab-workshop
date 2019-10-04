package main

import (
	"encoding/binary"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"

	"github.com/netsec-ethz/scion-apps/lib/scionutil"
	"github.com/scionproto/scion/go/lib/addr"
	"github.com/scionproto/scion/go/lib/sciond"
	"github.com/scionproto/scion/go/lib/snet"
)

// RECEPTION_BUFF_SIZE is the size of the buffer to read the packet from a client.
const RECEPTION_BUFF_SIZE = 1024 * 65

// PORT is the UDP port used to listen for incoming traffic.
const PORT = 12345

var localAddress *snet.Addr

// scoreBoard is a map[addr.IA] = uint64
var scoreBoard *sync.Map = new(sync.Map)

type ScoreEntry struct {
	Who        string
	NumPackets uint64
}

func fatal(err error) {
	panic(err)
}
func logError(format string, args ...interface{}) {
	fmt.Printf(format, args...)
}

func initNetwork() {
	localAddressStr, err := scionutil.GetLocalhostString()
	if err != nil {
		fatal(err)
	}
	localAddress, err = snet.AddrFromString(localAddressStr)
	if err != nil {
		fatal(err)
	}
	dispatcherPath := scionutil.GetDefaultDispatcher()
	sciondPath := sciond.GetDefaultSCIONDPath(nil)
	err = snet.Init(localAddress.IA, sciondPath, dispatcherPath)
	if err != nil {
		fatal(err)
	}
}

func handleClients(conn snet.Conn) {
	scoreChan := make(chan ScoreEntry)
	go handleScore(scoreChan)
	for {
		buffer := make([]byte, RECEPTION_BUFF_SIZE)
		n, clientAddr, err := conn.ReadFromSCION(buffer)
		if err != nil {
			logError("Error while reading from connection", err)
			continue
		}
		go handleClient(conn, buffer[:n], clientAddr)
		// keeping score here? Use a channel, to be prepared for when this is multi-threaded
		addr := fmt.Sprintf("%s,[%v]", clientAddr.IA, clientAddr.Host.L3)
		scoreChan <- ScoreEntry{
			Who:        addr,
			NumPackets: uint64(n),
		}
	}
}

// handleScore can handle the score board.
func handleScore(scoreChan chan ScoreEntry) {
	for {
		e := <-scoreChan
		board := scoreBoard
		actual, found := board.Load(e.Who)
		if !found {
			actual = interface{}(uint64(0))
		}
		s := actual.(uint64)
		s += e.NumPackets
		board.Store(e.Who, s)
	}
}

func handleClient(conn snet.Conn, buffer []byte, clientAddr *snet.Addr) {
	sendAck(conn, clientAddr, uint16(len(buffer)))
}

func sendAck(conn snet.Conn, clientAddr *snet.Addr, message uint16) {
	ackMessage := make([]byte, 2)
	binary.LittleEndian.PutUint16(ackMessage, message)
	_, err := conn.WriteTo(ackMessage, clientAddr)
	if err != nil {
		logError("Error sending ACK: %v", err)
	}
}

func dumpScoreBoard() {
	board := scoreBoard
	scoreBoard = new(sync.Map)
	fmt.Println("dumping score now")
	fileName := "/tmp/scores.txt"
	lines := make([]byte, 0)
	board.Range(func(_addr, _n interface{}) bool {
		addr := _addr.(string)
		n := _n.(uint64)
		lines = append(lines, ([]byte)(fmt.Sprintf("%s\t%d\n", addr, n))...)
		return true
	})
	err := ioutil.WriteFile(fileName, lines, 0644)
	if err != nil {
		logError("Error writing scores: %v", err)
	}
}

func initHTTP() {
	http.HandleFunc("/", httpHandler)
	go func() {
		if err := http.ListenAndServe(":8080", nil); err != nil {
			fatal(err)
		}
	}()
}

func httpHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case "POST":
		dumpScoreBoard()
		w.WriteHeader(http.StatusOK)
	default:
		w.WriteHeader(http.StatusBadRequest)
	}
}

func enableSigTermHandling() {
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGHUP)
	go func() {
		for {
			<-signals
			dumpScoreBoard()
		}
	}()
}

func main() {
	initNetwork()
	initHTTP()
	localAddress.Host.L4 = addr.NewL4UDPInfo(PORT)
	conn, err := snet.ListenSCION("udp4", localAddress)
	if err != nil {
		fatal(err)
	}
	enableSigTermHandling()
	handleClients(conn)
}
