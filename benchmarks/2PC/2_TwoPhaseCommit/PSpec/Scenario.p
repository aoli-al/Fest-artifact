scenario ConcurrentWriteThenRead(e0: eWriteTransReq, ef: eShutDown, e1: eWriteTransReq, e2: eReadTransReq) {
  e0.client != e1.client,
  e0.trans.key == e1.trans.key,
  e2.key == e1.trans.key
}
