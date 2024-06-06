event eRegisterWorker: int_sym;

machine Registry {
  var workerIds: set[int_sym];

  start state Init {
    on eRegisterWorker do (id: int_sym) {
      print format ("r{0}", id.value);
      workerIds += (id);
    }
  }
}
