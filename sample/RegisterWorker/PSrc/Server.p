machine Server {
  var reg: machine;

  start state Init {
    entry {
      var i: int;
      var w: machine;

      reg = new Registry();
      while (i < 3) {
        w = new Worker(i);
        send w, eWorkItem, reg;
        i = i + 1;
      }
    }
  }
}
