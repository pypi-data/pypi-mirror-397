!start.

sleep_time(3000). # milliseconds

generator_url("http://127.0.0.1:9990/").
validator_url("http://127.0.0.1:9999/").

spec("A function to compare two cities given their names and populations").

req_list([]).

+!start : spec(S) & generator_url(A) & req_list(L)<-
    .my_name(N) ;
    .print("Hello from", N) ;
    !request.

+!request : generator_url(A) & spec(S) & req_list(L) & sleep_time(T) <-
    .print("Sending reset to generator."); .send(A, achieve, reset);
     .wait(T) ;
    .print("Sending specification to generator."); .send(A,tell, spec(S)) ;
    .wait(T) ;
    .print("Sending current requirements to generator."); .send(A,tell, req_list(L)) ;
    .wait(T) ;
    .print("Sending build request to generator.");.send(A, achieve, build).

+reply(R) : validator_url(A) <-
    .print("Received the following requirement:", R) ;
    .print("Going to ask for validation.") ;
    -+tentative(R) ;
    !ask_validation(A,R).

+!ask_validation(A,R) : spec(S) <-
    .send_str(A,tell, S) ;
    .print("Just send a reminder of the specification.");
    .wait(3000) ;
    .print("Going to send the validation request.") ;
    .send_str_cb(A,propose,R, validation);
    .print("Validation request sent.").


+!validation("valid") : tentative(R) & req_list(L) <-
    .print("Received a validation. Update req list.") ;
    -req_list(L) ;
    +req_list([R|L]) ;
    .wait(3000) ;
    !request.

+!validation("invalid") <-
    .print("Received an invalidation.") ;
    !request.

+!validation("quit") :req_list(L) & spec(S) <-
    .print("Received a quit request.") ;
    .print("Initial specification:", S);
    .print("Final list of requirements:", L).

+!validation(Other) <-
    .print("Ignored message from the validation:", Other).

+reply_to(F) <-
    .print("Reply-to:", F).


+!reply_with_failure : reply_to(F) <-
    .my_name(N) ;
    .send(F, tell, failure(N)).


+failed(A) : selected(A) <-
    .print("Received: failure from", A);
    -selected(A) ;
    ?repository_url(R) ;
    .send(R, tell, failure(A)) ;
    .wait(3000) ;
    !request.

+failed(A) : not selected(A) <-
    .print("Warning: Received a failure about", A, "but that agent was not selected").

+failure : selected(A) <-
    .print("received failure message") ;
    -failure ;
    +failed(A).
