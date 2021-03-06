(require '[clojure.string :as str])


;;  master dict of opcode functions and program-counter properties
;;   key is opcode as a char, treating "99" as simply \9
;;   val is itself a dictionary of properties
(def opcodes
  {\1 {:ip-inc 4, :func #(+ (% 1) (% 2))}
   \2 {:ip-inc 4, :func #(* (% 1) (% 2))}
   \3 {:ip-inc 2, :func (fn [&x]
                          (print " input: ") (flush)
                          (Long/parseLong (read-line)))}
   \4 {:ip-inc 2, :func #(let [out (% 1)]
                           (println " the progam outputs:" out)
                           out)}       ;; also return what is printed
   \5 {:ip-inc 3, :func #(not= 0 (% 1))}
   \6 {:ip-inc 3, :func #(= 0 (% 1))}
   \7 {:ip-inc 4, :func #(if (< (% 1) (% 2)) 1 0)}
   \8 {:ip-inc 4, :func #(if (= (% 1) (% 2)) 1 0)}
   \9 {:ip-inc 1, :func #(identity %)}
   })


;;  parse an Intcode instruction
;;   return a vector of the opcode and its arguments
;;   internally, a dictionary of modal parameters is used
(defn parse-opcode [ram ip]
  (let [opcode    (ram ip)
        charcode  (vec (map char (str opcode)))       ;; Intcode as vec of chars
        positions (vec (map char (reverse "ABCDE")))  ;; modality position names, for keys
        parmsdict (loop [charstack (reverse charcode) ;; dictionary of ABCDE values
                         outdict   {}
                         counter   0]
                    (if (empty? charstack)     ;; before returning, create explicit leading zeroes
                      (loop [out      outdict
                             keystack (nthrest positions counter)]
                        (if (empty? keystack)
                          out
                          (recur (assoc out (first keystack) \0) (rest keystack))))
                      (recur                   ;; work through chars in the Intcode instr
                        (vec (rest charstack))
                        (assoc outdict (positions counter) ((vec (reverse charcode)) counter))
                        (inc counter))))
        offsets {\C 1, \B 2, \A 3}                    ;; relative location of value for mode args
        pos     (fn [charkey] (ram (ram (+ (offsets charkey) ip))))
        imm     (fn [charkey] (ram      (+ (offsets charkey) ip)))
        opchar  (parmsdict \E)]
    (case opchar
      (\1,\2,\7,\8)
         (vector opchar
                 (if (= \0 (parmsdict \C)) (pos \C) (imm \C))
                 (if (= \0 (parmsdict \B)) (pos \B) (imm \B))
                 (ram (+ 3 ip)))         ;; "will never be in immediate mode"
      \3 (vector opchar
                 (ram (+ 1 ip)))         ;; "will never be in immediate mode"
      \4 (vector opchar
                 (if (= \0 (parmsdict \C)) (pos \C) (imm \C)))
      (\5,\6)
         (vector opchar
                 (if (= \0 (parmsdict \C)) (pos \C) (imm \C))
                 (if (= \0 (parmsdict \B)) (pos \B) (imm \B)))
      \9 [opchar])))


;;  execution routine for a single operation
;;  look up the `func` in the `opcode` dict and act that func on
;;   the vector `instruction`, then `assoc` the func return into
;;   the RAM vector (or IP dict) at the appropriate address as
;;   per `(last instruction)`
;;  return a vector with two elements (perhaps a dict would be better?)
;;   -the dictionary that includes the new IP program counter
;;   -the possibly-updated RAM vector
(defn operate [ram dict-of-counters]
  (let [ip           (dict-of-counters :ip)  ;; lookup the current IP
        instruction  (parse-opcode ram ip)   ;; obtain vector of op char and int args
        opcode       (instruction 0)         ;;  the op char
        opcode-dict  (opcodes opcode)        ;; the properties of the current op
        operation    (opcode-dict :func)     ;;  the op function
        ip-increment (opcode-dict :ip-inc)]  ;;  the IP update amount
    (vector
      (case opcode                           ;; RAM return
        (\9,\5,\6)
           ram                               ;;  unaltered RAM for 99, 5, and 6
        \4 (do                               ;;  side-effect for 4 ...
             (operation instruction)
             ram)                            ;;   ...then return unaltered RAM
           (assoc                            ;;   else return altered RAM as per func
                  ram (last instruction) (operation instruction)))
      (case opcode                           ;; counter return
        \9 {}                                ;;  *** empty IP dict signals halt ***
        (\5,\6)                              ;;  5 & 6 func returns go to into IP dict
           (if (operation instruction)
             (assoc dict-of-counters
                    :ip (instruction 2))
             (assoc dict-of-counters
                    :ip (+ ip ip-increment)))
           (assoc                            ;;   else update counter(s)
                  dict-of-counters
                  :ip (+ ip ip-increment))))))



;;  run the program by recurring over RAM and IP until halt
(defn run-program [ram counters-dict]
  (if (empty? counters-dict)                 ;;  *** empty `counters-dict` signals halt ***
    ram                                      ;;  return RAM vector at halt
    (let [[a,b] (operate ram counters-dict)] ;;  else recur w/ destructured return
      (recur a b))))                         ;;   ?? how to recur w/o `let` destructuring ?
                                             ;;    perhaps if `operate` returned a dict ...
                                             ;;    bet the return would still be `let`ted ...


;;
;;  main program
;;

;;
;;   file I/O
;;    the program will be read into "RAM" as a vector for subsequent `assoc`s
(def intcode-program
  (let [file-contents (with-open
                        [f (clojure.java.io/reader "puzzle.txt")]
                        (str/trim (slurp f)))]
    (vec
      (for [c (str/split file-contents #"[,]")]
        (Long/parseLong c)))))

(println "Read" (count intcode-program) "Intcode ints from one line.")
;;   end file I/O
;;


;;
;;  run the Intcode program
;;
(println " at halt, memory address 0 holds:"
         (
          (run-program         ;; execute program, returning RAM vector at halt
            intcode-program    ;;  load the program into RAM
            {:ip 0, :base 0})  ;;  initialize counters
          0))                  ;; print zeroth element from returned RAM vec


