Parameter P Q R : Prop.
Theorem T' : (P -> Q -> R) -> P -> Q -> R.
Proof.
    exact (fun Hpqr Hp Hq => Hpqr Hp Hq).
Qed.

(*
; T' : (P Q R) [P Q -> R] P Q -> R 
(define (T' Hpqr Hp Hq)
    (Hpqr Hp Hq))
*)

Check false. 

Check True.

Print True.

Theorem T3 : (not (1 = 2)). 
Proof.
    unfold not.
    intros H.
    discriminate H.
Qed.

Definition and_1 (p: P /\ Q) : P :=
    match p with
    | conj Hp Hq => Hp
    end.

(* 
(define-struct conj [a b])
(define-contract (And P Q (Struct conj P Q))

(: and_1 (All (P Q) (-> (And P Q) P)))
(define (and_1 p)
    (conj-a p)))
*)

(*Theorem demorgan1 : forall P Q: Prop,
    not(P \/ Q) <-> not P /\ not Q.
Proof.
    intros P Q.
    split.
    constructor.
    - (* intros H.*)
    refine (fun H => _).
    unfold not in *.
    (* constructor *)
    refine (conj _ _).
    eauto.
    eauto.*)

Theorem demorganprop: forall P Q: bool,
    negb (orb P Q) = andb (negb P) (negb Q).
Proof.
    intros P Q.
    destruct P; destruct Q; reflexivity.
Qed.

Theorem demorganliteauto : forall P Q : Prop,
    not (P \/ Q) <-> not P /\ not Q.
Proof.
    intros P Q.
    constructor.
    - intros. constructor; info_eauto.
    - intros. destruct H. unfold not. intros. 
      destruct H1; eauto.
Qed.


Inductive ArithExp : Set :=
| num : nat -> ArithExp
| add : ArithExp -> ArithExp -> ArithExp.

Definition a1 := num 1.
Definition a2 := add (num 2) a1. 
Definition a4:= match a2 with
| add sub1 _ => sub1
| num _ => a1
 end.
    
Eval compute in a4.

Inductive ArithExp1 : Set :=
| num1 (n : nat)
| add1 (l r : ArithExp1).

Definition partial := (add (num 3)).
Definition a3 := partial (num 5).

Eval compute in a3.

Fixpoint eval (e : ArithExp) : nat :=
    match e with
    | num n => n
    | add e1 e2 => Nat.add (eval e1) (eval e2)
    end.

Eval compute in (eval a3).

Fixpoint const_fold (e : ArithExp) : ArithExp :=
    match e with
    | num n => num n
    | add l r =>
    match l, r with
    | num n1, num n2 => num (Nat.add n1 n2)
    | l', r' => add (const_fold l') (const_fold r')
    end
end.

Inductive Color : Set := 
| red : Color
| green : Color
| blue : Color.

Inductive RGB : Set :=
| mk :nat -> nat -> nat -> RGB.

Definition colorToRGB (c : Color) : RGB :=
    match c with
    | red => mk 255 0 0
    | green => mk 0 255 0
    | blue => mk 0 0 255
    end.

Definition RGBtoColor (r: RGB) : Color :=
    match r with
    | mk 255 0 0 => red
    | mk 0 255 0 => green
    | mk 0 0 255 => blue
    | _ => red
    end.

Theorem colorRGB_roundtrip : forall c,
    RGBtoColor (colorToRGB c) = c.
Proof.
    intros c.
    destruct c; reflexivity.
Qed.

Fixpoint double (n : nat) : nat :=
    match n with
    | 0 => 0
    | S n' => S (S (double n'))
    end.

Eval compute in double 10.

Theorem double_succ : forall n,
  double (S n) = S (S (double n)).   
Proof.
    intros n.
    simpl.
    reflexivity.
Qed.

Inductive ev : nat -> Prop :=
| ev_0 : ev 0
| ev_SS : forall n, 
   ev n -> ev (S (S n)). 

Fixpoint ev_pred (n : nat) : Prop :=
    match n with
    | 0 => True
    | S (S n) => ev_pred n'
    | _ => False
    end.

Theorem ev_4 : ev 4.
Proof. 
    apply ev_SS.
    apply ev_SS.
    apply ev_0.
Qed.

