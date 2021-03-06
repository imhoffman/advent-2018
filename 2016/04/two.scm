;;  options
;;   as per https://www.gnu.org/software/mit-scheme/documentation/mit-scheme-ref/Format.html
(load-option 'format)

;;  constants
;;   as a list, will string->list as needed for char-set
(define alpha "abcdefghijklmnopqrstuvwxyz")

;; empty list to eventually hold contents of input file
(define registry (list))
;; read in the file
;;  perhaps cons a (string line) rather than redefining registry,
;;  that way the close could be inside a lambda, a la
;;  https://scheme.com/tspl4/io.html#./io:h9
(define file (open-input-file "input.txt"))
(do ((line (read-line file) (read-line file))) ((eof-object? line))
        (set! registry (append registry (list line))))
(close-input-port file)


;;  recursive occurrence counter
(define counter
 (lambda (ch s)
  (let ((k (string-find-next-char s ch)))
   ;(format #t " checking for ~a in ~a~%" ch s)
   (if k
    (begin (if (= k (string-length s))
            1
            (+ 1 (counter ch (substring s (+ 1 k) (string-length s))))))
   0))))


;; return integer id from registry string
(define get-id
 (lambda (s)
  (let ( (id (substring s
              (string-find-next-char-in-set s char-set:numeric)
              (string-find-next-char s #\[))))
  (string->number id))))


;; checksum ruleset
(define sumcheck
 (lambda (s)
  (let ( (checksum (substring s
                    (+ 1 (string-find-next-char s #\[))
                    (string-find-next-char s #\])))
         (encrypted (substring s 0
                     (string-find-next-char-in-set s char-set:numeric)))
         (done #f) )
  (if (= 0 (counter
             (string-ref
               checksum
               (- (string-length checksum) 1))
             encrypted))
      (set! done #t))
    (for-each
     (lambda (ch)
       (if (and (not done) (or
            (> (counter ch encrypted)
               (counter (string-ref
                         checksum
                         (+ 1 (string-find-next-char checksum ch)))
                 encrypted))
            (and
             (= (counter ch encrypted)
                (counter (string-ref
                          checksum
                          (+ 1 (string-find-next-char checksum ch)))
                  encrypted))
             (< (string-find-next-char alpha ch)
                (string-find-next-char alpha
                      (string-ref checksum (+ 1 (string-find-next-char checksum ch))))))))
           (set! done #f) (set! done #t))
     )
     (reverse (cdr (reverse (string->list checksum)))))  ; loop over all but the final char
   ;; return
   (if done #f #t)
  )))
         

;; decryption ruleset
(define caesar
 (lambda (nrot)
  (lambda (ch)
   (let ( (loc (string-find-next-char alpha ch)) )
    (if (> (+ loc nrot) (- (string-length alpha) 1))
         (string-ref alpha (- (+ loc nrot) (string-length alpha)))
         (string-ref alpha (+ loc nrot)))))))

(define decrypted
 (lambda (s)
  (let ( (encrypted (substring s 0
                     (string-find-next-char-in-set s char-set:numeric)))
         (nrot (modulo (get-id s) (string-length alpha))))
  (list->string
   (map
    (lambda (ch)
     (if (char=? ch #\-)
          #\Space
          ((caesar nrot) ch)))
     (string->list encrypted))
  ))))


;;
;;  main program
(let ((total 0))
(for-each
 (lambda (s)
  (if (sumcheck s)
   (begin
    (set! total (+ total (get-id s)))
    (format #t " ~a ~a~%" (get-id s) (decrypted s))
   ))
 ) registry)
(format #t "~%  total of real sector ids: ~a~%~%" total))


(exit)

