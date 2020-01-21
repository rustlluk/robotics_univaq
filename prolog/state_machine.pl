upper_corner(0).
is_up :- upper_corner(C), x_pos(X), C==X.
is_down :- bottom_corner(C), x_pos(X), C==X.
is_left :- column(C), y_pos(Y), Y<C.
is_right :- column(C), y_pos(Y), Y>C.
x_pos(X) :- position(A), [X|_]=A.
y_pos(Y) :- position(A), [_|Z]=A, [Y|_]=Z.

stateMachine(state1) :- obs(X), X==1, !.
stateMachine(state2) :- is_up, !.
stateMachine(state3) :- is_down, !.
stateMachine(state4) :- is_right, !.
stateMachine(state5) :- is_left, !.
stateMachine(state6) :- !.
