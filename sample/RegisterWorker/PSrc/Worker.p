event eWorkItem: machine;

type int_sym     = (symtag: string, value: int);

machine Worker {
  var id: int_sym;

  start state Init {
    entry (arg: int) {
      id = (symtag = format("{0}", this), value = arg);
    }
    
    on eWorkItem do (reg: machine) {
      print format ("w{0}", id.value);
      send reg, eRegisterWorker, id;
    }
  }
}
