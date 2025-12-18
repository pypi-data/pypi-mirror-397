!start.


pingable_agent_address("http://127.0.0.1:9998").
pingable_file("receiver").

+!start <-
    .my_name(N) ;
    .print("Hello from", N) ;
    ?pingable_agent_address(A) ;
    !do_ping_ko(A) ;
    .wait(2000) ;
    !spawn_pingable ;
    ?actual_pingable_address(B) ;
    !do_ping_ok(B) .

+!do_ping_ko(DEST) : .is_alive(DEST, true) <-
    .print("Test KO : pingable agent should be detected as not alive.").

+!do_ping_ko(DEST) <-
    .print("Test OK : pingable agent detected as not alive.").

+!do_ping_ok(DEST) : .is_alive(DEST, true) <-
    .print ("Test OK : pingable agent detected alive").

+!do_ping_ok(DEST) <-
    .print("Test KO : pingable agent not detected as alive.").

+!ack(M) <- .print("Synchronous ack received (with content:",M,")").

# spawn
+!spawn_pingable : pingable_file(F)  <-
    .print("Going to spawn a pingable agent.") ;
    .spawn(F, A) ;
    +actual_pingable_address(A).

+!spawn_pingable <- .print("spawn_pingable : Missing parameters").

# log
+actual_pingable_address(A) <- .print("Registering pingable agent address:", A).
